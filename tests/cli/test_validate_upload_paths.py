from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

import falx.cli as cli
from tests.yaml_utils import safe_dump

runner = CliRunner()


def _write_seedance_i2v_config(config_path: Path, image_url: str) -> None:
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/image-to-video",
                "parameters": {
                    "prompt": "camera slowly pushes toward the subject",
                    "image_url": image_url,
                },
                "slug": "seedance-i2v-test",
                "version": 1,
            },
            allow_unicode=True,
        )
    )


@pytest.mark.parametrize("command", ["validate", "submit", "submit-async"])
def test_commands_reject_legacy_uploads_field(command: str, tmp_path: Path) -> None:
    asset_path = tmp_path / "\u591c\u5200\u795e.png"
    asset_path.write_bytes(b"fake image bytes")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/image-to-video",
                "parameters": {
                    "prompt": "camera slowly pushes toward the subject",
                },
                "slug": "seedance-i2v-test",
                "version": 1,
                "uploads": [
                    {
                        "target": "image_url",
                        "local_path": str(asset_path),
                        "original_name": "\u591c\u5200\u795e.png",
                    }
                ],
            },
            allow_unicode=True,
        )
    )

    result = runner.invoke(cli.app, [command, "--config", str(config_path)])

    assert result.exit_code == 1
    assert "uploads" in result.stderr
    assert "Extra inputs are not permitted" in result.stderr


def test_validate_accepts_local_path_in_url_field_without_uploads(tmp_path: Path) -> None:
    asset_path = tmp_path / "yatogami.png"
    asset_path.write_bytes(b"fake image bytes")
    config_path = tmp_path / "config.yaml"
    _write_seedance_i2v_config(config_path, str(asset_path))

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert result.stdout == "valid: bytedance/seedance-2.0/image-to-video\n"


def test_validate_rejects_missing_local_path_in_url_field_without_uploads(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.yaml"
    _write_seedance_i2v_config(config_path, str(tmp_path / "missing.png"))

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 1
    assert "URL fields must be public URLs or local file paths" in result.stderr


def test_validate_accepts_none_in_url_field_without_uploads(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/vidu/q3/image-to-video",
                "parameters": {
                    "prompt": "camera slowly pushes toward the subject",
                    "image_url": "https://example.com/source.png",
                    "end_image_url": None,
                },
                "slug": "vidu-q3-i2v-test",
                "version": 1,
            },
            allow_unicode=True,
        )
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert result.stdout == "valid: fal-ai/vidu/q3/image-to-video\n"


def test_validate_accepts_project_root_relative_path_resolved_against_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asset_dir = tmp_path / "workspace" / "demo-project" / "exp" / "G-0001_demo" / "assets"
    asset_dir.mkdir(parents=True)
    asset_path = asset_dir / "image.png"
    asset_path.write_bytes(b"payload")
    relative_path = "workspace/demo-project/exp/G-0001_demo/assets/image.png"
    config_path = tmp_path / ".nf" / "genweave" / "G-0001" / "job.yaml"
    config_path.parent.mkdir(parents=True)
    _write_seedance_i2v_config(config_path, relative_path)

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert result.stdout == "valid: bytedance/seedance-2.0/image-to-video\n"


def test_validate_allows_non_ascii_http_upload_target_url(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_seedance_i2v_config(
        config_path,
        "https://example.com/assets/\u591c\u5200\u795e.png",
    )

    result = runner.invoke(cli.app, ["validate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert result.stdout == "valid: bytedance/seedance-2.0/image-to-video\n"
