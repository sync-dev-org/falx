from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import falx.core as core
import falx.io as io
from falx.cli import app
from tests.conftest import FakeDownloader, FakeFalClient, JobStatus
from tests.yaml_utils import safe_dump, safe_load


def test_run_iter1_fake_e2e(
    tmp_path: Path,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0006_iter-one" / "output"
    config_path = tmp_path / "iter1.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/nano-banana-2/edit",
                "parameters": {
                    "prompt": "repair the orchestration seam",
                    "image_urls": [
                        "https://example.com/external.png",
                        "https://cdn.fal.local/sample_asset.png",
                    ],
                },
                "slug": "iter-one",
                "version": 1,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    fal_client.program_result(
        "req-0001",
        {"images": [{"url": "https://cdn.fal.local/req-0001.png"}]},
    )
    downloader = FakeDownloader()

    monkeypatch.setenv("FALX_OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr(core, "default_fal_client", lambda: fal_client, raising=False)
    monkeypatch.setattr(io, "default_downloader", lambda: downloader, raising=False)

    result = CliRunner().invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0.01"],
    )

    assert result.exit_code == 0
    assert result.stdout.startswith("request_id:")
    assert not result.stdout.lstrip().startswith("{")
    payload = safe_load(result.stdout)
    expected_path = (
        output_dir
        / "v1-1"
        / "G-0006_iter-one_v1-1-1.png"
    )
    assert payload == {
        "request_id": "req-0001",
        "status": "completed",
        "takes": [
            {
                "take": 1,
                "request_id": "req-0001",
                "batches": [{"batch": 1, "file_path": str(expected_path)}],
            }
        ],
    }
    updated_input = safe_load(config_path.read_text(encoding="utf-8"))
    assert updated_input["parameters"]["image_urls"] == [
        "https://example.com/external.png",
        "https://cdn.fal.local/sample_asset.png",
    ]
    assert "uploads" not in updated_input
    assert "results" not in updated_input

    assert len(downloader.downloads) == 1
    assert downloader.downloads[0] == ("https://cdn.fal.local/req-0001.png", expected_path)
