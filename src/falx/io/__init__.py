from __future__ import annotations

import functools
import hashlib
import mimetypes
import os
import re
import shutil
import tempfile
import unicodedata
from math import ceil, sqrt
from pathlib import Path
from typing import Any, NamedTuple, Protocol
from urllib.parse import urlparse

import httpx
from ruamel.yaml import YAML

from falx.models import (
    BaseFalConfig,
    JobConfig,
    validate_job_schema,
    validate_parameters,
)

_SAFE_YAML = YAML(typ="safe")
_SAFE_YAML.default_flow_style = False
_ENTRY_OUTPUT_DIR_RE = re.compile(r"^(?P<entry_id>G-\d{4})_.+")


class Uploader(Protocol):
    def upload(self, path: Path) -> str:
        """Upload a local file and return the resulting CDN URL."""


class Downloader(Protocol):
    def download(self, url: str, dest: Path) -> None:
        """Download a remote file into ``dest``."""


def validate_job_config(config: JobConfig) -> BaseFalConfig | None:
    _validate_url_fields_are_public_or_local_path(config.parameters)
    return validate_parameters(config.app_id, config.parameters)


class _FileSpec(NamedTuple):
    url: str
    file_name: str | None
    content_type: str | None
    output_index: int
    name_suffix: str | None


def _load_job_config_payload(path: Path) -> dict[str, Any]:
    payload = _SAFE_YAML.load(path.read_text()) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")

    return payload


def load_job_config(path: Path) -> JobConfig:
    return validate_job_schema(_load_job_config_payload(path))


def load_job_config_for_submit(path: Path) -> JobConfig:
    return load_job_config(path)


def place_result_files(
    result: dict[str, Any],
    *,
    output_dir: Path,
    app_id: str,
    slug: str,
    version: int,
    request_id: str,
    downloader: Downloader,
    take: int,
    cell: int | None = None,
    batch_start: int = 1,
) -> list[Path]:
    """Download result files into the canonical submit folder under ``output_dir``.

    Non-matrix outputs land in ``v<V>-<T>/``. Matrix outputs pass ``cell`` and
    land in ``c<C>-v<V>-<T>/``. The request id remains part of stdout /
    single-result metadata, but is intentionally absent from folder and file
    names.
    """
    _validate_positive_axis("batch_start", batch_start)
    job_dir = output_dir / _submit_folder_name(version=version, take=take, cell=cell)
    job_dir.mkdir(parents=True, exist_ok=True)

    file_specs = _collect_top_level_file_specs(result)
    written_paths: list[Path] = []
    base_stem = _result_file_stem(
        output_dir=output_dir,
        slug=slug,
        version=version,
        take=take,
        cell=cell,
    )

    for spec in file_specs:
        ext = _infer_extension(spec)
        batch = batch_start + spec.output_index - 1
        name_suffix = spec.name_suffix or ""
        destination = job_dir / f"{base_stem}-{batch}{name_suffix}{ext}"
        downloader.download(spec.url, destination)
        written_paths.append(destination)

    return written_paths


def _submit_folder_name(
    *,
    version: int,
    take: int,
    cell: int | None = None,
) -> str:
    _validate_positive_axis("version", version)
    _validate_positive_axis("take", take)
    if cell is None:
        return f"v{version}-{take}"
    _validate_positive_axis("cell", cell)
    return f"c{cell}-v{version}-{take}"


def _result_file_stem(
    *,
    output_dir: Path,
    slug: str,
    version: int,
    take: int,
    cell: int | None = None,
) -> str:
    identity = _output_identity_stem(output_dir=output_dir, slug=slug)
    if cell is None:
        return f"{identity}_v{version}-{take}"
    return f"{identity}_c{cell}_v{version}-{take}"


def _output_identity_stem(*, output_dir: Path, slug: str) -> str:
    parent_name = output_dir.parent.name
    if output_dir.name == "output" and _ENTRY_OUTPUT_DIR_RE.fullmatch(parent_name):
        return parent_name
    return slug


def _output_entry_id(output_dir: Path) -> str | None:
    parent_name = output_dir.parent.name
    if output_dir.name != "output":
        return None
    match = _ENTRY_OUTPUT_DIR_RE.fullmatch(parent_name)
    if match is None:
        return None
    return match.group("entry_id")


def _validate_positive_axis(name: str, value: int) -> None:
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")


def _app_id_stem(app_id: str) -> str:
    return app_id.replace("/", "_")


def write_contact_sheet_thumbnail(
    image_paths: list[Path],
    *,
    destination: Path,
) -> Path:
    if not image_paths:
        raise ValueError("image_paths must not be empty")

    import cv2
    import numpy as np

    images = []
    cell_width: int | None = None
    cell_height: int | None = None
    for path in image_paths:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"could not read image: {path}")
        height, width = image.shape[:2]
        scale = 0.5
        resized_width = round(width * scale)
        resized_height = round(height * scale)
        if cell_width is None or cell_height is None:
            cell_width = resized_width
            cell_height = resized_height
        elif (resized_width, resized_height) != (cell_width, cell_height):
            raise ValueError("all contact-sheet images must resolve to the same cell size")
        images.append(cv2.resize(image, (cell_width, cell_height), interpolation=cv2.INTER_AREA))

    if cell_width is None or cell_height is None:
        raise ValueError("image_paths must not be empty")

    cols = ceil(sqrt(len(images)))
    rows = ceil(len(images) / cols)
    canvas = np.zeros((cell_height * rows, cell_width * cols, 3), dtype=np.uint8)
    for index, image in enumerate(images):
        row, col = divmod(index, cols)
        y = row * cell_height
        x = col * cell_width
        canvas[y : y + cell_height, x : x + cell_width] = image

    destination.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(
        str(destination),
        canvas,
        [int(cv2.IMWRITE_JPEG_QUALITY), 90],
    )
    if not ok:
        raise RuntimeError(f"failed to write thumbnail: {destination}")
    return destination


def resolve_output_dir(
    cli_output: Path | None,
    config_output: str | Path | None,
) -> Path:
    raw_output = cli_output or config_output
    if isinstance(raw_output, str):
        raw_output = Path(raw_output)
    if raw_output is None:
        env_output = os.environ.get("FALX_OUTPUT_DIR")
        raw_output = Path(env_output) if env_output else None
    if raw_output is None:
        raise RuntimeError("output_dir must be set via --output, config, or FALX_OUTPUT_DIR")
    return raw_output.expanduser()


def default_uploader() -> Uploader:
    class _FalUploader:
        def upload(self, path: Path) -> str:
            import fal_client

            from falx.core import ensure_fal_key

            ensure_fal_key()
            return str(fal_client.upload_file(path))

    return _FalUploader()


def upload_file_to_cdn(path: Path, uploader: Uploader) -> str:
    local_path = path.expanduser().resolve()
    if not local_path.is_file():
        raise FileNotFoundError(str(path))

    suffix = local_path.suffix if local_path.suffix.isascii() else ".bin"
    ascii_name = _ascii_slugify(local_path.stem) + suffix
    if ascii_name == local_path.name:
        return uploader.upload(local_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir) / ascii_name
        shutil.copy2(local_path, temp_path)
        return uploader.upload(temp_path)


def default_downloader() -> Downloader:
    class _HTTPXDownloader:
        def download(self, url: str, dest: Path) -> None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with httpx.stream("GET", url) as response:
                response.raise_for_status()
                with dest.open("wb") as fh:
                    for chunk in response.iter_bytes():
                        fh.write(chunk)

    return _HTTPXDownloader()


def _is_url_key(key: Any) -> bool:
    if not isinstance(key, str):
        return False
    lower = key.lower()
    return lower.endswith(("url", "urls"))


def _validate_url_fields_are_public_or_local_path(
    value: Any,
    *,
    is_url_field: bool = False,
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _validate_url_fields_are_public_or_local_path(item, is_url_field=_is_url_key(key))
        return
    if isinstance(value, list):
        for item in value:
            _validate_url_fields_are_public_or_local_path(item, is_url_field=is_url_field)
        return
    if not is_url_field:
        return
    if value is None:
        return
    if isinstance(value, str) and _is_public_url(value):
        return
    if isinstance(value, str) and Path(value).expanduser().is_file():
        return
    raise ValueError(
        "URL fields must be public URLs or local file paths "
        f"(each value must be a public URL or local file path): {value!r}"
    )


def _is_public_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@functools.lru_cache(maxsize=1)
def _kakasi_converter() -> Any:
    import pykakasi

    return pykakasi.kakasi()


def _ascii_slugify(stem: str) -> str:
    transliterated = "".join(item["hepburn"] for item in _kakasi_converter().convert(stem))
    safe = unicodedata.normalize("NFKD", transliterated).encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", safe).strip("-._")
    if not safe:
        safe = f"asset-{hashlib.sha256(stem.encode('utf-8')).hexdigest()[:8]}"
    return safe


def _collect_top_level_file_specs(result: dict[str, Any]) -> list[_FileSpec]:
    specs: list[_FileSpec] = []
    next_index = 1
    items = list(result.items())
    position = 0

    while position < len(items):
        top_key, value = items[position]
        if _is_file_object(value):
            specs.append(_build_file_spec(value, next_index))
            next_index += 1
            position += 1
            continue

        if _is_file_list(value):
            arrays: list[list[dict[str, Any]]] = [value]
            lookahead = position + 1
            while lookahead < len(items):
                _, next_value = items[lookahead]
                if _is_file_list(next_value) and len(next_value) == len(value):
                    arrays.append(next_value)
                    lookahead += 1
                    continue
                break

            for item_index in range(len(value)):
                for array in arrays:
                    specs.append(_build_file_spec(array[item_index], next_index))
                next_index += 1

            position = lookahead
            continue

        if _is_nested_file_dict(value):
            specs.extend(_build_nested_file_specs(top_key, value, next_index))
            next_index += 1
            position += 1
            continue

        if _is_nested_file_dict_list(value):
            for nested_dict in value:
                specs.extend(_build_nested_file_specs(top_key, nested_dict, next_index))
                next_index += 1
            position += 1
            continue

        position += 1

    return specs


def _is_file_object(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("url"), str)


def _is_file_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_file_object(item) for item in value)


def _is_nested_file_dict(value: Any) -> bool:
    return isinstance(value, dict) and any(_is_file_object(item) for item in value.values())


def _is_nested_file_dict_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_is_nested_file_dict(item) for item in value)
    )


def _build_nested_file_specs(
    top_key: str,
    value: dict[str, Any],
    index: int,
) -> list[_FileSpec]:
    return [
        _build_file_spec(item, index, name_suffix=f"_{top_key}.{sub_key}")
        for sub_key, item in value.items()
        if _is_file_object(item)
    ]


def _build_file_spec(
    value: dict[str, Any],
    index: int,
    *,
    name_suffix: str | None = None,
) -> _FileSpec:
    file_name = value.get("file_name")
    content_type = value.get("content_type")
    return _FileSpec(
        url=value["url"],
        file_name=file_name if isinstance(file_name, str) else None,
        content_type=content_type if isinstance(content_type, str) else None,
        output_index=index,
        name_suffix=name_suffix,
    )


def _infer_extension(spec: _FileSpec) -> str:
    if spec.file_name:
        suffix = Path(spec.file_name).suffix
        if suffix:
            return suffix

    url_path = Path(urlparse(spec.url).path)
    if url_path.suffix:
        return url_path.suffix

    if spec.content_type:
        guessed = mimetypes.guess_extension(spec.content_type)
        if guessed:
            return guessed

    return ".bin"


__all__ = [
    "Downloader",
    "Uploader",
    "_app_id_stem",
    "default_downloader",
    "default_uploader",
    "load_job_config",
    "load_job_config_for_submit",
    "place_result_files",
    "resolve_output_dir",
    "upload_file_to_cdn",
    "write_contact_sheet_thumbnail",
]
