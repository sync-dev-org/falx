from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

import falx.cli as cli
from tests.yaml_utils import safe_dump

runner = CliRunner()


def _write_matrix_config(
    config_path: Path,
    *,
    parameters: dict[str, object],
    matrix_axes: dict[str, object],
    slug: str = "matrix-demo",
    version: int = 1,
) -> None:
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/text-to-video",
                "parameters": parameters,
                "slug": slug,
                "version": version,
                "matrix_axes": matrix_axes,
            },
            allow_unicode=True,
        )
    )


def test_validate_succeeds_on_well_formed_cartesian_matrix(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_matrix_config(
        config_path,
        parameters={
            "prompt": "placeholder",
            "aspect_ratio": "1:1",
        },
        matrix_axes={
            "mode": "cartesian",
            "axes": [
                {"field": "prompt", "values": ["A", "B"]},
                {"field": "aspect_ratio", "values": ["16:9", "1:1"]},
            ],
        },
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert "valid: bytedance/seedance-2.0/text-to-video (matrix: 4 cell(s))" in result.stdout
    assert "c1-v1-1 [ok]" in result.stdout
    assert "c4-v1-1 [ok]" in result.stdout


def test_validate_succeeds_on_multi_field_axis_matrix(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_matrix_config(
        config_path,
        parameters={
            "prompt": "placeholder",
            "aspect_ratio": "1:1",
            "resolution": "480p",
        },
        matrix_axes={
            "mode": "cartesian",
            "axes": [
                {
                    "fields": ["prompt", "aspect_ratio"],
                    "value_set": [["A", "16:9"], ["B", "1:1"]],
                },
                {"field": "resolution", "values": ["480p", "720p"]},
            ],
        },
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert "valid: bytedance/seedance-2.0/text-to-video (matrix: 4 cell(s))" in result.stdout
    assert "c1-v1-1 [ok] prompt='A', aspect_ratio='16:9', resolution='480p'" in result.stdout
    assert "c4-v1-1 [ok] prompt='B', aspect_ratio='1:1', resolution='720p'" in result.stdout


def test_validate_fail_fast_on_matrix_axes_referencing_unknown_parameter_field(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.yaml"
    _write_matrix_config(
        config_path,
        parameters={
            "prompt": "placeholder",
        },
        matrix_axes={
            "mode": "cartesian",
            "axes": [
                {"field": "aspect_ratio", "values": ["16:9", "1:1"]},
            ],
        },
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 1
    assert "matrix_axes.axes references unknown parameter" in result.stderr


def test_validate_fail_fast_when_multi_field_axis_references_unknown_parameter_field(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.yaml"
    _write_matrix_config(
        config_path,
        parameters={
            "prompt": "placeholder",
        },
        matrix_axes={
            "mode": "cartesian",
            "axes": [
                {"fields": ["prompt", "aspect_ratio"], "value_set": [["A", "16:9"]]},
            ],
        },
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 1
    assert "matrix_axes.axes references unknown parameter" in result.stderr


def test_validate_rejects_axis_with_field_and_fields_together(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_matrix_config(
        config_path,
        parameters={
            "prompt": "placeholder",
            "aspect_ratio": "1:1",
        },
        matrix_axes={
            "mode": "cartesian",
            "axes": [
                {
                    "field": "prompt",
                    "fields": ["prompt", "aspect_ratio"],
                    "values": ["A"],
                },
            ],
        },
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 1
    assert "field and fields" in result.stderr


def test_validate_passes_when_url_axis_resolves_to_existing_local_files_via_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "first.png").write_bytes(b"a")
    (tmp_path / "second.png").write_bytes(b"b")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/image-to-video",
                "parameters": {"prompt": "go", "image_url": "placeholder"},
                "slug": "url-matrix",
                "version": 1,
                "matrix_axes": {
                    "mode": "cartesian",
                    "axes": [
                        {"field": "image_url", "values": ["first.png", "second.png"]},
                    ],
                },
            },
            allow_unicode=True,
        )
    )

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert "matrix: 2 cell(s)" in result.stdout
    assert "c1-v1-1 [ok]" in result.stdout
    assert "c2-v1-1 [ok]" in result.stdout


def test_validate_fail_fast_when_one_url_axis_cell_misses_local_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "exists.png").write_bytes(b"a")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/image-to-video",
                "parameters": {"prompt": "go", "image_url": "placeholder"},
                "slug": "url-matrix-fail",
                "version": 1,
                "matrix_axes": {
                    "mode": "cartesian",
                    "axes": [
                        {"field": "image_url", "values": ["exists.png", "missing.png"]},
                    ],
                },
            },
            allow_unicode=True,
        )
    )

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 1
    assert "c1-v1-1 [ok]" in result.stderr
    assert "c2-v1-1 [fail]" in result.stderr
    assert "URL fields must be public URLs or local file paths" in result.stderr


def test_validate_rejects_zip_mode_until_stage_two_implemented(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_matrix_config(
        config_path,
        parameters={"prompt": "placeholder"},
        matrix_axes={
            "mode": "zip",
            "axes": [{"field": "prompt", "values": ["A", "B"]}],
        },
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 1
