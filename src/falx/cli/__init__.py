from __future__ import annotations

import asyncio
import copy
import json
import math
import random
import re
import warnings
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from io import StringIO
from pathlib import Path
from typing import Annotated, Any, Literal, NoReturn, Protocol, cast, get_args, get_origin

import httpx
import typer
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined
from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.comments import CommentedMap

import falx.core as core
import falx.io as io
import falx.matrix as matrix
from falx.models import JobConfig

APP_HELP = """falx submits fal.ai queue jobs from YAML configs and fetches generated assets.

Workflow:
  primary: falx run -c <yaml>
  resume: falx fetch -c <yaml> --request-id <id>
  local files: put file paths in URL fields; falx uploads them in memory

FAL_KEY must be set in the shell environment before online commands.

Output directory precedence: --output, then output_dir in YAML, then FALX_OUTPUT_DIR.

Exit codes:
  0 = all iterations succeeded
  1 = config, validation, or missing request_id
  2 = generation or fal API error
  3 = timeout or CDN retry exceeded

Offline commands: falx models, falx schema, falx validate.
"""

app = typer.Typer(help=APP_HELP)

_RANDOM_SEED_MIN = 0
_RANDOM_SEED_MAX = 2**31 - 1

_TRANSIENT_GENERATION_ERROR_TYPES = {
    "downstream_service_error",
    "gateway_timeout",
    "internal_error",
    "internal_server_error",
    "server_error",
    "service_unavailable",
    "temporary_unavailable",
    "timeout",
    "upstream_service_error",
}
_PERMANENT_GENERATION_ERROR_KEYWORDS = {
    "bad_request",
    "content_policy",
    "forbidden",
    "invalid",
    "not_found",
    "policy",
    "unauthorized",
    "validation",
}


def _is_transient_download_error(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.ReadTimeout, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        return status_code == 404 or 500 <= status_code < 600
    return False


def _is_transient_generation_error(error_type: str | None, detail: str | None) -> bool:
    normalized_type = (error_type or "").lower()
    normalized_detail = (detail or "").lower()
    if any(keyword in normalized_type for keyword in _PERMANENT_GENERATION_ERROR_KEYWORDS):
        return False
    if normalized_type in _TRANSIENT_GENERATION_ERROR_TYPES:
        return True
    return not any(
        keyword in normalized_detail for keyword in _PERMANENT_GENERATION_ERROR_KEYWORDS
    ) and any(keyword in normalized_detail for keyword in _TRANSIENT_GENERATION_ERROR_TYPES)


RUN_HELP = (
    "Submit, poll, and download results in one async pipeline. With --iterations=N or "
    "matrix_axes, concurrent submits are capped at max_concurrency (default 8). "
    "If interrupted, re-run `falx run` to continue: matrix resumes within the same "
    "take for pending cells only; non-matrix re-runs progress to new take folders. "
    "Or fetch individual requests with `falx fetch --request-id <id>`. "
    "exit codes: 0=all succeeded; 1=config/validation/missing request_id; "
    "2=generation/fal error; 3=timeout/CDN retry exceeded."
)
FETCH_HELP = (
    "Fetch one submitted request by --request-id, download completed result files, "
    "and print stdout YAML."
)
CANCEL_HELP = "Cancel one submitted request by --request-id and print stdout YAML."
MODELS_HELP = "List registered model app_id values. Does not call the fal API (offline)."
SCHEMA_HELP = "Print a YAML example for top-level JobConfig. Does not call the fal API (offline)."
VALIDATE_HELP = (
    "Validate the YAML config only; do not submit. Success exits 0, invalid configs "
    "exit 1. Does not call the fal API (offline)."
)
UPLOAD_HELP = "Upload one or more local files to fal CDN and print '<path>\\t<url>' TSV lines."

_SUBMIT_DEPRECATION = (
    "warning: `falx submit` is a deprecated alias for `falx run`; use `falx run` directly."
)
_SUBMIT_ASYNC_DEPRECATION = (
    "warning: `falx submit-async` is a deprecated alias for `falx run` (polling-aware "
    "concurrent submit pipeline); use `falx run` directly."
)

CONFIG_OPTION = typer.Option(
    ...,
    "--config",
    "-c",
    exists=True,
    dir_okay=False,
    help="YAML job config file to process (required).",
)
OUTPUT_OPTION = typer.Option(
    None,
    "--output",
    "-o",
    file_okay=False,
    help=(
        "Result output directory. If omitted, falx uses output_dir in YAML or the "
        "FALX_OUTPUT_DIR environment variable. Missing directories are created when "
        "writing results."
    ),
)
REQUEST_ID_OPTION = typer.Option(
    ...,
    "--request-id",
    help="fal queue request_id returned by `falx run`.",
)
SLUG_OPTION = typer.Option(
    None,
    "--slug",
    help="Output filename slug. If omitted, falx uses slug in YAML.",
)
VERSION_OPTION = typer.Option(
    None,
    "--version",
    min=1,
    help="Output version number. If omitted, falx uses version in YAML or 1.",
)
TAKE_FETCH_OPTION = typer.Option(
    1,
    "--take",
    min=1,
    help="Take number to write into output filenames for fetch.",
)
ITERATIONS_OPTION = typer.Option(
    None,
    "--iterations",
    "-n",
    min=1,
    help=(
        "Submit N identical configs concurrently to generate variations (min=1). "
        "If omitted, falx uses iterations in YAML or defaults to 1."
    ),
)
MAX_CONCURRENCY_OPTION = typer.Option(
    None,
    "--max-concurrency",
    min=1,
    help=(
        "Maximum concurrent in-flight submits to fal.ai. If omitted, falx uses "
        "max_concurrency in YAML or defaults to 8."
    ),
)
TIMEOUT_OPTION = typer.Option(
    1800.0,
    "--timeout",
    help=(
        "Polling timeout per submit in seconds. This is not the total timeout for "
        "all concurrent submits. Default: 1800."
    ),
)
POLL_INTERVAL_OPTION = typer.Option(
    5.0,
    "--poll-interval",
    help="Polling interval in seconds. Default: 5.",
)

_SAFE_YAML = YAML(typ="safe")
_SAFE_YAML.default_flow_style = False
_STDOUT_YAML = YAML()
_STDOUT_YAML.default_flow_style = False
_STDOUT_YAML.indent(mapping=2, sequence=4, offset=2)


class SubmitHandleLike(Protocol):
    request_id: str


class JobStatusLike(Protocol):
    state: str
    error: str | None
    error_type: str | None


@dataclass(frozen=True)
class FetchSuccess:
    index: int
    paths: list[Path]


_NON_MATRIX_TAKE_RE = re.compile(r"^v(?P<version>[1-9]\d*)-(?P<take>[1-9]\d*)$")
_MATRIX_TAKE_RE = re.compile(
    r"^c(?P<cell>[1-9]\d*)-v(?P<version>[1-9]\d*)-(?P<take>[1-9]\d*)$"
)


def _module_attr(module: object, name: str) -> Any:
    try:
        return getattr(module, name)
    except AttributeError as exc:
        raise RuntimeError(f"Required dependency is not available: {name}") from exc


def _echo_error(message: str, *, code: int) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(code=code)


def _load_env() -> None:
    load_dotenv()


def _load_config(config_path: Path) -> JobConfig:
    loader = _module_attr(io, "load_job_config")
    try:
        return cast(JobConfig, loader(config_path))
    except ValidationError as exc:
        _echo_error(_format_validation_error(exc), code=1)
    except (ValueError, YAMLError) as exc:
        _echo_error(f"{config_path}: {exc}", code=1)


def _load_config_for_submit(config_path: Path, cli_iterations: int | None) -> JobConfig:
    loader = _module_attr(io, "load_job_config")
    try:
        loaded = cast(JobConfig, loader(config_path))
    except ValidationError:
        submit_loader = _module_attr(io, "load_job_config_for_submit")
        try:
            loaded = cast(JobConfig, submit_loader(config_path))
        except ValidationError as exc:
            _echo_error(_format_validation_error(exc), code=1)
        except (ValueError, YAMLError) as exc:
            _echo_error(f"{config_path}: {exc}", code=1)
    except (ValueError, YAMLError) as exc:
        _echo_error(f"{config_path}: {exc}", code=1)

    return loaded


def _build_client() -> object:
    factory = _module_attr(core, "default_fal_client")
    try:
        return factory()
    except RuntimeError as exc:
        _echo_error(str(exc), code=1)


def _format_fal_error(exc: Exception) -> str:
    error_type = getattr(exc, "error_type", None)
    detail = getattr(exc, "detail", str(exc))
    if error_type:
        return f"error_type: {error_type}\ndetail: {detail}"
    return str(detail)


def _format_validation_error(exc: ValidationError) -> str:
    return _dump_safe_yaml(exc.errors(include_context=False, include_url=False)).rstrip()


def _dump_safe_yaml(payload: Any) -> str:
    buffer = StringIO()
    _SAFE_YAML.dump(payload, buffer)
    return buffer.getvalue()


def _print_stdout_yaml(payload: dict[str, Any]) -> None:
    buffer = StringIO()
    _STDOUT_YAML.dump(payload, buffer)
    typer.echo(buffer.getvalue(), nl=False)


def _batch_payloads(paths: list[Path], *, batch_start: int = 1) -> list[dict[str, Any]]:
    return [
        {
            "batch": index,
            "file_path": str(path),
        }
        for index, path in enumerate(paths, start=batch_start)
    ]


def _take_payload(
    *,
    take: int,
    request_id: str,
    paths: list[Path] | None = None,
    batch_start: int = 1,
    error: str | None = None,
    error_type: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "take": take,
        "request_id": request_id,
        "batches": _batch_payloads(paths or [], batch_start=batch_start),
    }
    if error is not None:
        payload["error"] = error
    if error_type is not None:
        payload["error_type"] = error_type
    return payload


def _stdout_payload(
    *,
    request_id: str,
    status: str,
    takes: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "takes": takes,
        "status": status,
    }


def _resolve_slug(config: JobConfig, cli_slug: str | None) -> str:
    return cli_slug or config.slug


def _resolve_version(config: JobConfig, cli_version: int | None) -> int:
    return cli_version or config.version


def _resolve_max_concurrency(config: JobConfig, cli_max_concurrency: int | None) -> int:
    if cli_max_concurrency is not None:
        return cli_max_concurrency
    return config.max_concurrency


def _existing_take_numbers(output_dir: Path) -> list[int]:
    if not output_dir.is_dir():
        return []
    takes: list[int] = []
    for child in output_dir.iterdir():
        if not child.is_dir():
            continue
        match = _NON_MATRIX_TAKE_RE.fullmatch(child.name) or _MATRIX_TAKE_RE.fullmatch(child.name)
        if match is None:
            continue
        takes.append(int(match.group("take")))
    return takes


def _existing_matrix_take_numbers(output_dir: Path, *, version: int) -> list[int]:
    if not output_dir.is_dir():
        return []
    takes: list[int] = []
    for child in output_dir.iterdir():
        if not child.is_dir():
            continue
        match = _MATRIX_TAKE_RE.fullmatch(child.name)
        if match is None:
            continue
        if int(match.group("version")) != version:
            continue
        takes.append(int(match.group("take")))
    return takes


def _next_take(output_dir: Path) -> int:
    takes = _existing_take_numbers(output_dir)
    if not takes:
        return 1
    return max(takes) + 1


def _matrix_take_for_submit(
    *,
    cells: list[matrix.CompiledCell],
    output_dir: Path,
    version: int,
) -> int:
    takes = _existing_matrix_take_numbers(output_dir, version=version)
    if not takes:
        return 1

    latest_take = max(takes)
    pending = matrix.pending_cells(
        cells=cells,
        output_dir=output_dir,
        version=version,
        take=latest_take,
    )
    completed_count = len(cells) - len(pending)
    if 0 < completed_count < len(cells):
        return latest_take
    return latest_take + 1


def _echo_captured_warnings(caught: list[warnings.WarningMessage]) -> None:
    for warning in caught:
        typer.echo(f"warning: {warning.message}", err=True)


def _load_models_module() -> object:
    return import_module("falx.models")


def _iter_config_classes(models_module: object) -> list[type[Any]]:
    fal_config = _module_attr(models_module, "FalConfig")
    union_type = get_args(fal_config)[0] if get_origin(fal_config) is Annotated else fal_config
    return list(get_args(union_type))


def _config_class_for_app_id(models_module: object, app_id: str) -> type[Any] | None:
    for config_class in _iter_config_classes(models_module):
        app_id_field = config_class.model_fields["app_id"]
        if app_id in get_args(app_id_field.annotation):
            return config_class
    return None


def _random_seed_field_for_config(config: JobConfig) -> str | None:
    config_class = _config_class_for_app_id(_load_models_module(), config.app_id)
    if config_class is None:
        return None
    seed_field = getattr(config_class, "random_seed_field", None)
    if seed_field is not None and seed_field not in config_class.model_fields:
        raise RuntimeError(
            f"{config.app_id} random_seed_field {seed_field!r} is not a parameter field"
        )
    return cast(str | None, seed_field)


def _random_iteration_seed() -> int:
    return random.randint(_RANDOM_SEED_MIN, _RANDOM_SEED_MAX)


def _parameters_with_iteration_seed(
    config: JobConfig,
    uploaded_parameters: dict[str, Any],
) -> tuple[dict[str, Any], int | None]:
    seed_field = _random_seed_field_for_config(config)
    if seed_field is None:
        return uploaded_parameters, None

    seed = uploaded_parameters.get(seed_field)
    if seed is not None:
        return uploaded_parameters, cast(int, seed)

    seeded_parameters = copy.deepcopy(uploaded_parameters)
    seed = _random_iteration_seed()
    seeded_parameters[seed_field] = seed
    return seeded_parameters, seed


def _uploaded_url_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    uploader: Any | None = None
    upload_file_to_cdn = _module_attr(io, "upload_file_to_cdn")
    uploader_factory = _module_attr(io, "default_uploader")

    def upload(value: Any, *, is_url_field: bool = False) -> Any:
        nonlocal uploader
        if isinstance(value, dict):
            return {key: upload(item, is_url_field=_is_url_key(key)) for key, item in value.items()}
        if isinstance(value, list):
            return [upload(item, is_url_field=is_url_field) for item in value]
        if not is_url_field:
            return copy.deepcopy(value)
        if isinstance(value, str) and _is_public_url(value):
            return copy.deepcopy(value)

        if isinstance(value, str):
            local_path = Path(value).expanduser()
            if local_path.is_file():
                if uploader is None:
                    uploader = uploader_factory()
                return cast(str, upload_file_to_cdn(local_path, uploader))
        raise ValueError(
            "URL fields must be public URLs or local file paths "
            f"(each value must be a public URL or local file path): {value!r}"
        )

    return cast(dict[str, Any], upload(parameters))


def _uploaded_url_parameters_or_exit(parameters: dict[str, Any]) -> dict[str, Any]:
    try:
        return _uploaded_url_parameters(parameters)
    except (OSError, ValueError) as exc:
        _echo_error(str(exc), code=1)


def _cell_job_config(config: JobConfig, cell: matrix.CompiledCell, cell_dir: Path) -> JobConfig:
    """Build a single-cell JobConfig used to feed cell submit pipelines."""
    return JobConfig(
        app_id=config.app_id,
        parameters=cell.parameters,
        output_dir=str(cell_dir),
        iterations=1,
        slug=config.slug,
        version=config.version,
        max_concurrency=config.max_concurrency,
        output_expiration_seconds=config.output_expiration_seconds,
    )


def _matrix_cell_payload(
    *,
    cell: matrix.CompiledCell,
    request_id: str,
    status: str,
    take: int,
    paths: list[Path] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "cell": cell.cell,
        "coords": dict(cell.coords),
        "request_id": request_id,
        "status": status,
        "takes": [{"take": take, "batches": _batch_payloads(paths or [])}],
    }
    return payload


def _matrix_stdout_payload(
    *,
    status: str,
    cells: list[dict[str, Any]],
    skipped_cells: list[tuple[int, int]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "matrix": True,
        "status": status,
        "cells": cells,
    }
    if skipped_cells:
        payload["skipped_cells"] = [{"cell": cell, "take": take} for cell, take in skipped_cells]
    return payload


def _format_matrix_validation_summary(
    summary: matrix.ValidationSummary, *, version: int
) -> str:
    lines: list[str] = []
    for result in summary.cell_results:
        marker = "ok" if result.ok else "fail"
        coords_repr = ", ".join(f"{key}={value!r}" for key, value in result.coords.items())
        subdir = matrix.cell_subdir_name(result.cell, version, take=1)
        lines.append(f"{subdir} [{marker}] {coords_repr}")
        if not result.ok and result.error:
            lines.append(f"  error: {result.error}")
    return "\n".join(lines)


def _is_url_key(key: Any) -> bool:
    is_url_key = getattr(io, "_is_url_key", None)
    if is_url_key is not None:
        return cast(bool, is_url_key(key))
    if not isinstance(key, str):
        return False
    return key.lower().endswith(("url", "urls"))


def _is_public_url(value: str) -> bool:
    is_public_url = getattr(io, "_is_public_url", None)
    if is_public_url is not None:
        return cast(bool, is_public_url(value))
    return value.startswith(("http://", "https://"))


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _write_single_result_yaml(
    *,
    config: JobConfig,
    uploaded_parameters: dict[str, Any],
    output_dir: Path,
    payload_output_dir: Path,
    slug: str,
    version: int,
    request_id: str,
    seed: int | None,
    submitted_at: str | None,
    completed_at: str,
    raw_result: dict[str, Any],
    take: int,
    cell: int | None = None,
) -> Path:
    payload: dict[str, Any] = {
        "app_id": config.app_id,
        "iterations": 1,
        "output_dir": str(payload_output_dir),
        "parameters": uploaded_parameters,
    }
    if config.output_expiration_seconds is not None:
        payload["output_expiration_seconds"] = config.output_expiration_seconds
    result_entry = {
        "completed_at": completed_at,
        "request_id": request_id,
        "result": raw_result,
        "seed": seed,
        "submitted_at": submitted_at,
    }

    destination = _single_result_yaml_path(
        output_dir=output_dir,
        version=version,
        take=take,
        slug=slug,
        cell=cell,
    )
    if destination.exists():
        existing = _SAFE_YAML.load(destination.read_text()) or {}
        if isinstance(existing, dict) and isinstance(existing.get("results"), list):
            payload["results"] = [*existing["results"], result_entry]
        else:
            payload["results"] = [result_entry]
    else:
        payload["results"] = [result_entry]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(_dump_safe_yaml(payload), encoding="utf-8")
    return destination


def _single_result_yaml_path(
    *,
    output_dir: Path,
    version: int,
    take: int,
    slug: str,
    cell: int | None = None,
) -> Path:
    folder = io._submit_folder_name(version=version, take=take, cell=cell)
    identity = io._output_identity_stem(output_dir=output_dir, slug=slug)
    return output_dir / folder / f"{identity}.yaml"


def _build_schema_example_yaml(config_class: type[Any], app_id: str) -> str:
    example = CommentedMap()
    example["app_id"] = app_id
    example["parameters"] = _build_parameters_example(config_class)
    example["output_dir"] = "<absolute output directory>"
    example["slug"] = "<kebab-case-output-slug>"
    example["version"] = 1
    example["iterations"] = 1
    example["max_concurrency"] = 8

    _apply_field_comment(example, JobConfig.model_fields["app_id"], "app_id")
    _apply_field_comment(example, JobConfig.model_fields["parameters"], "parameters")
    _apply_field_comment(example, JobConfig.model_fields["output_dir"], "output_dir")
    _apply_field_comment(example, JobConfig.model_fields["slug"], "slug")
    _apply_field_comment(example, JobConfig.model_fields["version"], "version")
    _apply_field_comment(example, JobConfig.model_fields["iterations"], "iterations")
    _apply_field_comment(example, JobConfig.model_fields["max_concurrency"], "max_concurrency")

    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    buffer = StringIO()
    yaml.dump(example, buffer)
    return buffer.getvalue()


def _build_parameters_example(config_class: type[Any]) -> CommentedMap:
    parameters = CommentedMap()
    overrides = getattr(config_class, "schema_example_parameters", {})
    for field_name, field in config_class.model_fields.items():
        if field_name == "app_id":
            continue
        parameters[field_name] = (
            copy.deepcopy(overrides[field_name])
            if field_name in overrides
            else _field_example_value(field_name, field)
        )
        _apply_field_comment(parameters, field, field_name, indent=2)
    return parameters


def _field_example_value(field_name: str, field: Any) -> Any:
    if not field.is_required():
        default_factory = getattr(field, "default_factory", None)
        if default_factory is not None:
            return default_factory()
        if field.default is not PydanticUndefined:
            return field.default
    return _placeholder_for_required_field(field_name, field)


def _placeholder_for_required_field(field_name: str, field: Any) -> Any:
    annotation = field.annotation
    origin = get_origin(annotation)
    if origin is Literal:
        return get_args(annotation)[0]
    if field_name == "prompt":
        return "<your prompt here>"
    if field_name.endswith("_urls"):
        return ["https://example.com/input"]
    if field_name.endswith("_url") or field_name.endswith("_image_url"):
        return "https://example.com/input"

    if origin in (list, tuple, set):
        min_length = max(
            (getattr(metadata, "min_length", 0) or 0 for metadata in field.metadata),
            default=0,
        )
        item_annotation = get_args(annotation)[0]
        return [_placeholder_for_annotation(item_annotation) for _ in range(min_length)]
    if annotation is bool:
        return False
    if annotation in (int, float):
        return _numeric_example_value(annotation, field)
    return f"<{field_name}>"


def _numeric_example_value(annotation: type[int] | type[float], field: Any) -> int | float:
    value = annotation(1)
    for metadata in field.metadata:
        if (bound := getattr(metadata, "ge", None)) is not None:
            value = max(value, math.ceil(bound) if annotation is int else bound)
        if (bound := getattr(metadata, "gt", None)) is not None:
            value = max(
                value,
                math.floor(bound) + 1 if annotation is int else math.nextafter(bound, math.inf),
            )
        if (bound := getattr(metadata, "le", None)) is not None:
            value = min(value, math.floor(bound) if annotation is int else bound)
        if (bound := getattr(metadata, "lt", None)) is not None:
            value = min(
                value,
                math.ceil(bound) - 1 if annotation is int else math.nextafter(bound, -math.inf),
            )
    return annotation(value)


def _placeholder_for_annotation(annotation: object) -> Any:
    if get_origin(annotation) is Literal:
        return get_args(annotation)[0]
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return {
            field_name: _field_example_value(field_name, field)
            for field_name, field in annotation.model_fields.items()
            if field_name != "app_id"
        }
    if annotation is bool:
        return False
    if annotation is int:
        return 1
    if annotation is float:
        return 1.0
    return "<item>"


def _apply_field_comment(
    mapping: CommentedMap,
    field: Any,
    key: str,
    *,
    indent: int = 0,
) -> None:
    if field.description:
        mapping.yaml_set_comment_before_after_key(key, before=field.description, indent=indent)


def _resolve_output_dir(
    *,
    cli_output: Path | None,
    config_output: str | Path | None,
) -> Path:
    resolver = _module_attr(io, "resolve_output_dir")
    try:
        return cast(Path, resolver(cli_output, config_output))
    except RuntimeError as exc:
        _echo_error(str(exc), code=1)


def _validate_job_config(config: JobConfig) -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        validate_job_config = getattr(io, "validate_job_config", None)
        if validate_job_config is not None:
            validate_job_config(config)
        else:
            models = _load_models_module()
            validate_parameters = _module_attr(models, "validate_parameters")
            validate_parameters(config.app_id, config.parameters)
    _echo_captured_warnings(caught)


def _submit_headers(config: JobConfig) -> dict[str, str] | None:
    if config.output_expiration_seconds is None:
        return None
    return {
        "X-Fal-Object-Lifecycle-Preference": json.dumps(
            {"expiration_duration_seconds": config.output_expiration_seconds},
            separators=(",", ":"),
        )
    }


def _resolved_iterations(config: JobConfig, cli_iterations: int | None) -> int:
    if cli_iterations is not None:
        return cli_iterations
    return config.iterations


_STILL_IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}


def _configured_num_images(config: JobConfig) -> int:
    value = config.parameters.get("num_images", 1)
    if isinstance(value, int):
        return value
    return 1


def _configured_output_format_is_still_image(config: JobConfig) -> bool:
    value = config.parameters.get("output_format")
    if not isinstance(value, str):
        return True
    return f".{value.lower()}" in _STILL_IMAGE_SUFFIXES


def _all_run_outputs_are_still_images(successes: list[FetchSuccess]) -> bool:
    paths = [path for success in successes for path in success.paths]
    return bool(paths) and all(path.suffix.lower() in _STILL_IMAGE_SUFFIXES for path in paths)


def _with_run_contact_sheet_thumbnails(
    *,
    config: JobConfig,
    successes: list[FetchSuccess],
) -> list[FetchSuccess]:
    if _configured_num_images(config) <= 1:
        return successes
    if not _configured_output_format_is_still_image(config):
        return successes
    if not _all_run_outputs_are_still_images(successes):
        return successes

    write_contact_sheet_thumbnail = _module_attr(io, "write_contact_sheet_thumbnail")
    updated_successes: list[FetchSuccess] = []
    for success in successes:
        if len(success.paths) <= 1:
            updated_successes.append(success)
            continue

        contact_stem = re.sub(r"-\d+$", "", success.paths[0].stem)
        destination = success.paths[0].with_name(f"{contact_stem}_contact.jpg")
        thumbnail_path = cast(
            Path,
            write_contact_sheet_thumbnail(success.paths, destination=destination),
        )
        updated_successes.append(
            FetchSuccess(
                index=success.index,
                paths=[*success.paths, thumbnail_path],
            )
        )
    return updated_successes


# -----------------------------------------------------------------------------
# Async submit pipeline
# -----------------------------------------------------------------------------


class _CellTimeout(Exception):
    """Raised when a cell-level submit-poll exceeds its per-cell timeout."""

    def __init__(self, request_id: str) -> None:
        super().__init__(f"timeout waiting for request_id={request_id}")
        self.request_id = request_id


class _CellGenerationError(Exception):
    """Raised when fal reports completion with an error for one cell or take."""

    def __init__(self, request_id: str, error: str | None, error_type: str | None) -> None:
        super().__init__(error or "generation error")
        self.request_id = request_id
        self.error = error
        self.error_type = error_type


async def _submit_one_async(
    *,
    config: JobConfig,
    iteration_parameters: dict[str, Any],
    client: Any,
) -> SubmitHandleLike:
    try:
        handle = await core.submit(
            config.app_id,
            iteration_parameters,
            client=client,
            headers=_submit_headers(config),
        )
    except Exception as exc:
        if hasattr(exc, "detail") or hasattr(exc, "error_type"):
            _echo_error(_format_fal_error(exc), code=2)
        raise
    return cast(SubmitHandleLike, handle)


async def _poll_until_complete_async(
    *,
    app_id: str,
    request_id: str,
    client: Any,
    timeout: float,
    poll_interval: float,
) -> JobStatusLike:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while True:
        try:
            status = cast(
                JobStatusLike,
                await core.fetch_status(app_id, request_id, client=client),
            )
        except Exception as exc:
            if hasattr(exc, "detail") or hasattr(exc, "error_type"):
                _echo_error(_format_fal_error(exc), code=2)
            raise

        if status.state == "COMPLETED":
            return status
        if loop.time() >= deadline:
            raise _CellTimeout(request_id)
        await asyncio.sleep(poll_interval)


async def _download_one_async(
    *,
    config: JobConfig,
    uploaded_parameters: dict[str, Any],
    request_id: str,
    output_dir: Path,
    slug: str,
    version: int,
    take: int,
    seed: int | None,
    submitted_at: str,
    client: Any,
    cell: int | None = None,
    payload_output_dir: Path | None = None,
    batch_start: int = 1,
) -> list[Path]:
    fetch_result = _module_attr(core, "fetch_result")
    downloader_factory = _module_attr(io, "default_downloader")
    place_result_files = _module_attr(io, "place_result_files")
    raw_result = cast(
        dict[str, Any],
        await fetch_result(config.app_id, request_id, client=client),
    )
    paths = cast(
        list[Path],
        place_result_files(
            raw_result,
            output_dir=output_dir,
            app_id=config.app_id,
            slug=slug,
            version=version,
            request_id=request_id,
            downloader=downloader_factory(),
            take=take,
            cell=cell,
            batch_start=batch_start,
        ),
    )
    _write_single_result_yaml(
        config=config,
        uploaded_parameters=uploaded_parameters,
        output_dir=output_dir,
        payload_output_dir=payload_output_dir or output_dir,
        slug=slug,
        version=version,
        take=take,
        request_id=request_id,
        seed=seed,
        submitted_at=submitted_at,
        completed_at=_now_iso(),
        raw_result=raw_result,
        cell=cell,
    )
    return paths


@dataclass
class _CellRunResult:
    cell: matrix.CompiledCell
    request_id: str
    paths: list[Path]
    seed: int | None
    submitted_at: str
    error: str | None = None
    error_type: str | None = None
    timed_out: bool = False


async def _run_matrix_cell_async(
    *,
    config: JobConfig,
    cell: matrix.CompiledCell,
    output_dir: Path,
    slug: str,
    version: int,
    take: int,
    client: Any,
    semaphore: asyncio.Semaphore,
    timeout: float,
    poll_interval: float,
) -> _CellRunResult:
    cell_dir = output_dir / matrix.cell_subdir_name(cell.cell, version, take=take)
    matrix.write_compiled_child(config=config, cell=cell, output_dir=output_dir, take=take)
    cell_config = _cell_job_config(config, cell, cell_dir)
    uploaded_parameters = _uploaded_url_parameters_or_exit(cell_config.parameters)
    iteration_parameters, seed = _parameters_with_iteration_seed(cell_config, uploaded_parameters)
    submitted_at = _now_iso()

    async with semaphore:
        handle = await _submit_one_async(
            config=cell_config, iteration_parameters=iteration_parameters, client=client
        )
        try:
            status = await _poll_until_complete_async(
                app_id=cell_config.app_id,
                request_id=handle.request_id,
                client=client,
                timeout=timeout,
                poll_interval=poll_interval,
            )
        except _CellTimeout:
            return _CellRunResult(
                cell=cell,
                request_id=handle.request_id,
                paths=[],
                seed=seed,
                submitted_at=submitted_at,
                timed_out=True,
            )

        if status.error:
            return _CellRunResult(
                cell=cell,
                request_id=handle.request_id,
                paths=[],
                seed=seed,
                submitted_at=submitted_at,
                error=status.error,
                error_type=status.error_type,
            )

        paths = await _download_one_async(
            config=cell_config,
            uploaded_parameters=uploaded_parameters,
            request_id=handle.request_id,
            output_dir=output_dir,
            slug=slug,
            version=version,
            take=take,
            seed=seed,
            submitted_at=submitted_at,
            client=client,
            cell=cell.cell,
            payload_output_dir=cell_dir,
        )

    return _CellRunResult(
        cell=cell,
        request_id=handle.request_id,
        paths=paths,
        seed=seed,
        submitted_at=submitted_at,
    )


async def _run_matrix_async(
    config: JobConfig,
    *,
    output_dir: Path,
    slug: str,
    version: int,
    max_concurrency: int,
    timeout: float,
    poll_interval: float,
) -> None:
    try:
        matrix.validate_matrix_or_raise(config)
    except matrix.MatrixValidationError as exc:
        typer.echo(
            _format_matrix_validation_summary(exc.summary, version=config.version), err=True
        )
        _echo_error(str(exc), code=1)

    cells = matrix.compile_cells(config)
    take = _matrix_take_for_submit(
        cells=cells,
        output_dir=output_dir,
        version=config.version,
    )
    pending = matrix.pending_cells(
        cells=cells,
        output_dir=output_dir,
        version=config.version,
        take=take,
    )
    skipped = [(cell.cell, take) for cell in cells if cell not in pending]

    if not pending:
        _print_stdout_yaml(
            _matrix_stdout_payload(
                status="completed",
                cells=[],
                skipped_cells=skipped,
            )
        )
        return

    client = _build_client()
    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = [
        _run_matrix_cell_async(
            config=config,
            cell=cell,
            output_dir=output_dir,
            slug=slug,
            version=version,
            take=take,
            client=client,
            semaphore=semaphore,
            timeout=timeout,
            poll_interval=poll_interval,
        )
        for cell in pending
    ]
    results = await asyncio.gather(*tasks)

    cell_payloads = [
        _cell_payload_from_run_result(result, take=take)
        for result in sorted(results, key=lambda r: r.cell.cell)
    ]

    if any(r.timed_out for r in results):
        _print_stdout_yaml(
            _matrix_stdout_payload(
                status="in_progress",
                cells=cell_payloads,
                skipped_cells=skipped,
            )
        )
        raise typer.Exit(3)
    if any(r.error for r in results):
        _print_stdout_yaml(
            _matrix_stdout_payload(
                status="failed",
                cells=cell_payloads,
                skipped_cells=skipped,
            )
        )
        raise typer.Exit(2)

    _print_stdout_yaml(
        _matrix_stdout_payload(
            status="completed",
            cells=cell_payloads,
            skipped_cells=skipped,
        )
    )


def _cell_payload_from_run_result(result: _CellRunResult, *, take: int) -> dict[str, Any]:
    if result.timed_out:
        status = "in_progress"
    elif result.error:
        status = "failed"
    else:
        status = "completed"
    return _matrix_cell_payload(
        cell=result.cell,
        request_id=result.request_id,
        status=status,
        take=take,
        paths=result.paths or None,
    )


@dataclass
class _TakeRunResult:
    take: int
    request_id: str
    paths: list[Path]
    seed: int | None
    submitted_at: str
    error: str | None = None
    error_type: str | None = None
    timed_out: bool = False


async def _run_take_async(
    *,
    config: JobConfig,
    uploaded_parameters: dict[str, Any],
    output_dir: Path,
    slug: str,
    version: int,
    take: int,
    client: Any,
    semaphore: asyncio.Semaphore,
    timeout: float,
    poll_interval: float,
) -> _TakeRunResult:
    iteration_parameters, seed = _parameters_with_iteration_seed(config, uploaded_parameters)
    submitted_at = _now_iso()

    async with semaphore:
        try:
            handle = await _submit_one_async(
                config=config, iteration_parameters=iteration_parameters, client=client
            )
        except Exception as exc:
            return _TakeRunResult(
                take=take,
                request_id="",
                paths=[],
                seed=seed,
                submitted_at=submitted_at,
                error=str(exc),
                error_type=type(exc).__name__,
            )

        try:
            status = await _poll_until_complete_async(
                app_id=config.app_id,
                request_id=handle.request_id,
                client=client,
                timeout=timeout,
                poll_interval=poll_interval,
            )
        except _CellTimeout:
            return _TakeRunResult(
                take=take,
                request_id=handle.request_id,
                paths=[],
                seed=seed,
                submitted_at=submitted_at,
                timed_out=True,
            )

        if status.error:
            return _TakeRunResult(
                take=take,
                request_id=handle.request_id,
                paths=[],
                seed=seed,
                submitted_at=submitted_at,
                error=status.error,
                error_type=status.error_type,
            )

        try:
            paths = await _download_one_async(
                config=config,
                uploaded_parameters=uploaded_parameters,
                request_id=handle.request_id,
                output_dir=output_dir,
                slug=slug,
                version=version,
                take=take,
                seed=seed,
                submitted_at=submitted_at,
                client=client,
            )
        except Exception as exc:
            return _TakeRunResult(
                take=take,
                request_id=handle.request_id,
                paths=[],
                seed=seed,
                submitted_at=submitted_at,
                error=str(exc),
                error_type=type(exc).__name__,
            )

    return _TakeRunResult(
        take=take,
        request_id=handle.request_id,
        paths=paths,
        seed=seed,
        submitted_at=submitted_at,
    )


async def _run_non_matrix_async(
    config: JobConfig,
    *,
    output_dir: Path,
    slug: str,
    version: int,
    iterations: int,
    max_concurrency: int,
    timeout: float,
    poll_interval: float,
) -> None:
    try:
        _validate_job_config(config)
    except ValidationError as exc:
        _echo_error(_format_validation_error(exc), code=1)
    except ValueError as exc:
        _echo_error(str(exc), code=1)

    uploaded_parameters = _uploaded_url_parameters_or_exit(config.parameters)
    base_take = _next_take(output_dir)
    client = _build_client()
    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = [
        _run_take_async(
            config=config,
            uploaded_parameters=uploaded_parameters,
            output_dir=output_dir,
            slug=slug,
            version=version,
            take=base_take + offset,
            client=client,
            semaphore=semaphore,
            timeout=timeout,
            poll_interval=poll_interval,
        )
        for offset in range(iterations)
    ]
    results = sorted(await asyncio.gather(*tasks), key=lambda r: r.take)

    take_payloads = [
        _take_payload(
            take=r.take,
            request_id=r.request_id,
            paths=r.paths or None,
            error=r.error,
            error_type=r.error_type,
        )
        for r in results
    ]
    first_request_id = next(
        (r.request_id for r in results if r.request_id),
        results[0].request_id,
    )

    if any(r.timed_out for r in results):
        _print_stdout_yaml(
            _stdout_payload(
                request_id=first_request_id,
                status="in_progress",
                takes=take_payloads,
            )
        )
        raise typer.Exit(3)
    if any(r.error for r in results):
        _print_stdout_yaml(
            _stdout_payload(
                request_id=first_request_id,
                status="failed",
                takes=take_payloads,
            )
        )
        raise typer.Exit(2)

    fetch_successes = [
        FetchSuccess(index=index, paths=r.paths) for index, r in enumerate(results)
    ]
    _with_run_contact_sheet_thumbnails(
        config=config,
        successes=fetch_successes,
    )
    _print_stdout_yaml(
        _stdout_payload(
            request_id=first_request_id,
            status="completed",
            takes=take_payloads,
        )
    )


def _run_pipeline(
    config_path: Path,
    *,
    output: Path | None,
    cli_slug: str | None,
    cli_version: int | None,
    cli_iterations: int | None,
    cli_max_concurrency: int | None,
    timeout: float,
    poll_interval: float,
) -> None:
    _load_env()
    loaded = _load_config_for_submit(config_path, cli_iterations)
    output_dir = _resolve_output_dir(cli_output=output, config_output=loaded.output_dir)
    resolved_slug = _resolve_slug(loaded, cli_slug)
    resolved_version = _resolve_version(loaded, cli_version)
    resolved_max_concurrency = _resolve_max_concurrency(loaded, cli_max_concurrency)

    if loaded.matrix_axes is not None:
        asyncio.run(
            _run_matrix_async(
                loaded,
                output_dir=output_dir,
                slug=resolved_slug,
                version=resolved_version,
                max_concurrency=resolved_max_concurrency,
                timeout=timeout,
                poll_interval=poll_interval,
            )
        )
        return

    resolved_iterations = _resolved_iterations(loaded, cli_iterations)
    asyncio.run(
        _run_non_matrix_async(
            loaded,
            output_dir=output_dir,
            slug=resolved_slug,
            version=resolved_version,
            iterations=resolved_iterations,
            max_concurrency=resolved_max_concurrency,
            timeout=timeout,
            poll_interval=poll_interval,
        )
    )


# -----------------------------------------------------------------------------
# Async fetch / cancel helpers
# -----------------------------------------------------------------------------


async def _fetch_request_payload_async(
    *,
    config: JobConfig,
    request_id: str,
    output_dir: Path,
    slug: str,
    version: int,
    take: int,
) -> dict[str, Any]:
    client = _build_client()
    try:
        status = cast(
            JobStatusLike,
            await core.fetch_status(config.app_id, request_id, client=client),
        )
    except Exception as exc:
        if hasattr(exc, "detail") or hasattr(exc, "error_type"):
            _echo_error(_format_fal_error(exc), code=2)
        raise

    if status.state != "COMPLETED":
        return _stdout_payload(
            request_id=request_id,
            status="in_progress",
            takes=[_take_payload(take=take, request_id=request_id)],
        )

    if status.error:
        return _stdout_payload(
            request_id=request_id,
            status="failed",
            takes=[_take_payload(take=take, request_id=request_id)],
        )

    try:
        uploaded_parameters = _uploaded_url_parameters_or_exit(config.parameters)
        paths = await _download_one_async(
            config=config,
            uploaded_parameters=uploaded_parameters,
            request_id=request_id,
            output_dir=output_dir,
            slug=slug,
            version=version,
            take=take,
            seed=None,
            submitted_at=_now_iso_placeholder_for_fetch(),
            client=client,
        )
    except Exception as exc:
        if hasattr(exc, "detail") or hasattr(exc, "error_type"):
            _echo_error(_format_fal_error(exc), code=2)
        raise
    return _stdout_payload(
        request_id=request_id,
        status="completed",
        takes=[
            _take_payload(take=take, request_id=request_id, paths=paths),
        ],
    )


def _now_iso_placeholder_for_fetch() -> str | None:
    return None


async def _cancel_async(app_id: str, request_id: str) -> None:
    client = _build_client()
    try:
        await core.cancel(app_id, request_id, client=client)
    except Exception as exc:
        if hasattr(exc, "detail") or hasattr(exc, "error_type"):
            _echo_error(_format_fal_error(exc), code=2)
        raise


# -----------------------------------------------------------------------------
# Typer commands
# -----------------------------------------------------------------------------


@app.command(help=UPLOAD_HELP)
def upload(
    files: Annotated[
        list[Path],
        typer.Argument(
            help="Local files to upload. Each successful file prints '<path>\\t<cdn_url>'."
        ),
    ],
) -> None:
    """Upload local files to fal CDN and print TSV lines for successful uploads."""
    _load_env()
    uploader_factory = _module_attr(io, "default_uploader")
    upload_file_to_cdn = _module_attr(io, "upload_file_to_cdn")
    uploader = uploader_factory()
    failed = False
    for file_path in files:
        try:
            cdn_url = upload_file_to_cdn(file_path, uploader)
        except Exception as exc:
            failed = True
            typer.echo(f"{file_path}: {exc}", err=True)
            continue
        typer.echo(f"{file_path}\t{cdn_url}")
    if failed:
        raise typer.Exit(1)


@app.command(help=FETCH_HELP)
def fetch(
    config: Path = CONFIG_OPTION,
    output: Path | None = OUTPUT_OPTION,
    request_id: str = REQUEST_ID_OPTION,
    slug: str | None = SLUG_OPTION,
    version: int | None = VERSION_OPTION,
    take: int = TAKE_FETCH_OPTION,
) -> None:
    """Fetch one request by request_id and print stdout YAML."""
    _load_env()
    loaded = _load_config(config)
    output_dir = _resolve_output_dir(cli_output=output, config_output=loaded.output_dir)
    payload = asyncio.run(
        _fetch_request_payload_async(
            config=loaded,
            request_id=request_id,
            output_dir=output_dir,
            slug=_resolve_slug(loaded, slug),
            version=_resolve_version(loaded, version),
            take=take,
        )
    )
    _print_stdout_yaml(payload)
    if payload["status"] == "failed":
        raise typer.Exit(2)


@app.command(help=CANCEL_HELP)
def cancel(
    config: Path = CONFIG_OPTION,
    request_id: str = REQUEST_ID_OPTION,
) -> None:
    """Cancel one request by request_id and print stdout YAML."""
    _load_env()
    loaded = _load_config(config)
    asyncio.run(_cancel_async(loaded.app_id, request_id))
    _print_stdout_yaml({"request_id": request_id, "status": "cancelled"})


@app.command(help=MODELS_HELP)
def models() -> None:
    """List registered model app_id values without calling the fal API."""
    _load_env()
    supported_app_ids = _module_attr(_load_models_module(), "SUPPORTED_APP_IDS")
    for app_id in sorted(cast(set[str] | frozenset[str], supported_app_ids)):
        typer.echo(app_id)


@app.command(help=SCHEMA_HELP)
def schema(app_id: str) -> None:
    """Print a top-level JobConfig YAML example without calling the fal API."""
    _load_env()
    models_module = _load_models_module()
    config_class = _config_class_for_app_id(models_module, app_id)
    if config_class is None:
        _echo_error(
            f"Unknown app_id: {app_id}\nRun `falx models` to list supported app_id values.",
            code=1,
        )
    typer.echo(_build_schema_example_yaml(config_class, app_id), nl=False)


@app.command(help=VALIDATE_HELP)
def validate(
    config: Path = CONFIG_OPTION,
) -> None:
    """Validate the YAML config without submitting or calling the fal API.

    Success exits 0; invalid configs exit 1.
    """
    _load_env()
    loaded = _load_config(config)

    if loaded.matrix_axes is not None:
        try:
            summary = matrix.validate_matrix_or_raise(loaded)
        except matrix.MatrixValidationError as exc:
            typer.echo(
                _format_matrix_validation_summary(exc.summary, version=loaded.version), err=True
            )
            _echo_error(str(exc), code=1)
        typer.echo(_format_matrix_validation_summary(summary, version=loaded.version))
        typer.echo(f"valid: {loaded.app_id} (matrix: {len(summary.cell_results)} cell(s))")
        return

    try:
        _validate_job_config(loaded)
    except ValidationError as exc:
        _echo_error(_format_validation_error(exc), code=1)
    except ValueError as exc:
        _echo_error(str(exc), code=1)

    typer.echo(f"valid: {loaded.app_id}")


@app.command("run", help=RUN_HELP)
def run(
    config: Path = CONFIG_OPTION,
    output: Path | None = OUTPUT_OPTION,
    timeout: float = TIMEOUT_OPTION,
    poll_interval: float = POLL_INTERVAL_OPTION,
    slug: str | None = SLUG_OPTION,
    version: int | None = VERSION_OPTION,
    iterations: int | None = ITERATIONS_OPTION,
    max_concurrency: int | None = MAX_CONCURRENCY_OPTION,
) -> None:
    """Run async submit + poll + download pipeline with max_concurrency control."""
    _run_pipeline(
        config,
        output=output,
        cli_slug=slug,
        cli_version=version,
        cli_iterations=iterations,
        cli_max_concurrency=max_concurrency,
        timeout=timeout,
        poll_interval=poll_interval,
    )


@app.command("submit", deprecated=True, help="DEPRECATED: alias for `falx run`.")
def submit(
    config: Path = CONFIG_OPTION,
    output: Path | None = OUTPUT_OPTION,
    timeout: float = TIMEOUT_OPTION,
    poll_interval: float = POLL_INTERVAL_OPTION,
    slug: str | None = SLUG_OPTION,
    version: int | None = VERSION_OPTION,
    iterations: int | None = ITERATIONS_OPTION,
    max_concurrency: int | None = MAX_CONCURRENCY_OPTION,
) -> None:
    """Deprecated alias of `falx run`. Emits a warning then runs the same pipeline."""
    typer.echo(_SUBMIT_DEPRECATION, err=True)
    _run_pipeline(
        config,
        output=output,
        cli_slug=slug,
        cli_version=version,
        cli_iterations=iterations,
        cli_max_concurrency=max_concurrency,
        timeout=timeout,
        poll_interval=poll_interval,
    )


@app.command("submit-async", deprecated=True, help="DEPRECATED: alias for `falx run`.")
def submit_async(
    config: Path = CONFIG_OPTION,
    output: Path | None = OUTPUT_OPTION,
    iterations: int | None = ITERATIONS_OPTION,
    max_concurrency: int | None = MAX_CONCURRENCY_OPTION,
    timeout: float = TIMEOUT_OPTION,
    poll_interval: float = POLL_INTERVAL_OPTION,
) -> None:
    """Deprecated alias of `falx run`. Emits a warning then runs the polling pipeline."""
    typer.echo(_SUBMIT_ASYNC_DEPRECATION, err=True)
    _run_pipeline(
        config,
        output=output,
        cli_slug=None,
        cli_version=None,
        cli_iterations=iterations,
        cli_max_concurrency=max_concurrency,
        timeout=timeout,
        poll_interval=poll_interval,
    )
