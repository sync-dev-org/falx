"""Parameter matrix sweep module.

Provides cartesian expansion, compiled child job files, fail-fast validation,
and cell-level resume. Each cartesian axis can synchronize multiple parameter
fields via fields/value_set. Zip mode and matrix_grid post-processing are not
supported.
"""

from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from ruamel.yaml import YAML

import falx.io as io
from falx.models import JobConfig, validate_job_schema

_SAFE_YAML = YAML(typ="safe")
_SAFE_YAML.default_flow_style = False


@dataclass(frozen=True)
class CompiledCell:
    """A single cell of an expanded matrix run: index, axis coordinates, parameters."""

    cell: int
    coords: dict[str, Any]
    parameters: dict[str, Any]


@dataclass(frozen=True)
class CellValidationResult:
    cell: int
    coords: dict[str, Any]
    ok: bool
    error: str | None = None


@dataclass(frozen=True)
class ValidationSummary:
    """Per-cell validation outcomes for a matrix run."""

    cell_results: list[CellValidationResult]

    @property
    def ok(self) -> bool:
        return all(result.ok for result in self.cell_results)

    @property
    def failed(self) -> list[CellValidationResult]:
        return [result for result in self.cell_results if not result.ok]


class MatrixValidationError(ValueError):
    """Raised when one or more cells fail validation during a matrix run."""

    def __init__(self, summary: ValidationSummary) -> None:
        self.summary = summary
        failed_count = len(summary.failed)
        total = len(summary.cell_results)
        super().__init__(f"matrix validation failed: {failed_count}/{total} cell(s) invalid")


def cell_subdir_name(cell: int, version: int, take: int = 1) -> str:
    """Return the deterministic directory name for a given cell + version + take."""
    if cell < 1:
        raise ValueError(f"cell must be >= 1, got {cell}")
    if version < 1:
        raise ValueError(f"version must be >= 1, got {version}")
    if take < 1:
        raise ValueError(f"take must be >= 1, got {take}")
    return f"c{cell}-v{version}-{take}"


def compile_cells(config: JobConfig) -> list[CompiledCell]:
    """Expand matrix_axes via cartesian product into per-cell parameters.

    Returns an empty list when matrix_axes is absent (single-submit mode).
    """
    if config.matrix_axes is None:
        return []
    axes = config.matrix_axes.axes
    cells: list[CompiledCell] = []
    for index, combo in enumerate(
        itertools.product(*(axis.replacement_groups for axis in axes)),
        start=1,
    ):
        coords: dict[str, Any] = {}
        parameters = copy.deepcopy(config.parameters)
        for axis, values in zip(axes, combo, strict=True):
            for field, value in zip(axis.parameter_fields, values, strict=True):
                coords[field] = value
                if value is not None:
                    parameters[field] = value
        cells.append(CompiledCell(cell=index, coords=coords, parameters=parameters))
    return cells


def compiled_child_payload(
    config: JobConfig,
    cell: CompiledCell,
    *,
    take: int = 1,
) -> dict[str, Any]:
    """Build the wrapper-schema-conformant payload for a single cell's child job.yaml.

    The compiled child:
      - drops matrix_axes
      - substitutes the cell's coords into parameters
      - pins iterations to 1
      - rewrites output_dir to the cell's subdir so the child can be re-submitted standalone
    """
    payload: dict[str, Any] = {
        "app_id": config.app_id,
        "parameters": cell.parameters,
        "iterations": 1,
        "slug": config.slug,
        "version": config.version,
    }
    if config.output_dir is not None:
        subdir = cell_subdir_name(cell.cell, config.version, take)
        payload["output_dir"] = f"{config.output_dir.rstrip('/')}/{subdir}"
    if config.output_expiration_seconds is not None:
        payload["output_expiration_seconds"] = config.output_expiration_seconds
    return payload


def write_compiled_child(
    *,
    config: JobConfig,
    cell: CompiledCell,
    output_dir: Path,
    take: int = 1,
) -> Path:
    """Materialize the compiled child job.yaml under output/c<C>-v<V>-<T>/.

    Returns the absolute path to the written child file.
    """
    subdir = cell_subdir_name(cell.cell, config.version, take)
    cell_dir = output_dir / subdir
    cell_dir.mkdir(parents=True, exist_ok=True)
    child_path = cell_dir / _compiled_child_yaml_name(output_dir=output_dir, subdir=subdir)
    payload = compiled_child_payload(config, cell, take=take)
    with child_path.open("w") as fh:
        _SAFE_YAML.dump(payload, fh)
    return child_path


def _compiled_child_yaml_name(*, output_dir: Path, subdir: str) -> str:
    entry_id = io._output_entry_id(output_dir)
    if entry_id is None:
        return f"{subdir}-job.yaml"
    return f"{entry_id}_{subdir}-job.yaml"


def validate_matrix(config: JobConfig) -> ValidationSummary:
    """Compile every cell, validate each as a standalone JobConfig.

    Per-cell validation runs:
      1. `validate_job_schema` to confirm the compiled child parses as a valid
         JobConfig (= top-level schema check, matrix_axes stripped, iterations=1).
      2. `io.validate_job_config` to confirm the wrapper-config Pydantic schema
         (e.g. registered model parameter constraints) and URL field resolution
         hold cell-by-cell.

    URL field resolution uses the working directory of the process running falx
    as the base for relative paths.
    """
    if config.matrix_axes is None:
        return ValidationSummary(cell_results=[])
    cells = compile_cells(config)
    results: list[CellValidationResult] = []
    for cell in cells:
        payload = compiled_child_payload(config, cell)
        try:
            child_config = validate_job_schema(payload)
        except (ValidationError, ValueError) as exc:
            results.append(
                CellValidationResult(
                    cell=cell.cell,
                    coords=cell.coords,
                    ok=False,
                    error=str(exc),
                )
            )
            continue
        try:
            io.validate_job_config(child_config)
        except (ValidationError, ValueError) as exc:
            results.append(
                CellValidationResult(
                    cell=cell.cell,
                    coords=cell.coords,
                    ok=False,
                    error=str(exc),
                )
            )
            continue
        results.append(
            CellValidationResult(cell=cell.cell, coords=cell.coords, ok=True, error=None)
        )
    return ValidationSummary(cell_results=results)


def validate_matrix_or_raise(config: JobConfig) -> ValidationSummary:
    """Run `validate_matrix` and raise `MatrixValidationError` on any failed cell.

    Returned summary always reflects all cells when no failure occurs; the raised
    error carries the same summary for the caller to inspect.
    """
    summary = validate_matrix(config)
    if not summary.ok:
        raise MatrixValidationError(summary)
    return summary


def cell_is_completed(cell_dir: Path) -> bool:
    """Return True when a cell's output directory contains at least one materialized
    wrapper-output file beyond its own compiled child yaml.

    Used by the resume path to skip already-finished cells. The compiled child
    yaml lives at `<cell_dir>/G-NNNN_<cell_dir.name>-job.yaml` for G-entry
    output directories, with `<cell_dir>/<cell_dir.name>-job.yaml` retained as
    a generic fallback; any other sibling file or any descendant file indicates
    that the wrapper has
    materialized output. The caller is responsible for picking a version-aware
    `cell_dir` (= `output_dir / cell_subdir_name(cell, version, take)`) so that
    same-entry version progression does not collide with prior-version output.
    """
    if not cell_dir.is_dir():
        return False
    child_yaml_names = {f"{cell_dir.name}-job.yaml"}
    entry_id = io._output_entry_id(cell_dir.parent)
    if entry_id is not None:
        child_yaml_names.add(f"{entry_id}_{cell_dir.name}-job.yaml")
    for entry in cell_dir.rglob("*"):
        if not entry.is_file():
            continue
        if entry.parent == cell_dir and entry.name in child_yaml_names:
            continue
        return True
    return False


def pending_cells(
    *,
    cells: list[CompiledCell],
    output_dir: Path,
    version: int,
    take: int = 1,
) -> list[CompiledCell]:
    """Filter compiled cells to those that have not yet produced wrapper output
    for the given `version` / `take`.

    A cell is considered completed when `cell_is_completed` returns True for
    `output_dir/c<C>-v<V>-<T>/`. Returns the cells that still need to be
    submitted in original order. Prior-version and prior-take directories are
    ignored so that each (version, take) group has its own resume boundary.
    """
    pending: list[CompiledCell] = []
    for cell in cells:
        cell_dir = output_dir / cell_subdir_name(cell.cell, version, take)
        if cell_is_completed(cell_dir):
            continue
        pending.append(cell)
    return pending


__all__ = [
    "CellValidationResult",
    "CompiledCell",
    "MatrixValidationError",
    "ValidationSummary",
    "cell_is_completed",
    "cell_subdir_name",
    "compile_cells",
    "compiled_child_payload",
    "pending_cells",
    "validate_matrix",
    "validate_matrix_or_raise",
    "write_compiled_child",
]
