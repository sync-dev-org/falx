from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import falx.core as core
import falx.io as io
from falx.cli import app
from tests.conftest import FakeDownloader, FakeFalClient, JobStatus
from tests.yaml_utils import safe_dump, safe_load


def test_run_iter_n_fake_e2e(
    tmp_path: Path,
    monkeypatch,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0007_iter-many" / "output"
    config_path = tmp_path / "iter-n.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/nano-banana-2/edit",
                "parameters": {
                    "prompt": "hold request order steady",
                    "image_urls": [
                        "https://example.com/external.png",
                        "https://cdn.fal.local/sample_asset.png",
                    ],
                },
                "slug": "iter-many",
                "version": 1,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    fal_client = FakeFalClient()
    programmed_request_ids = ["req-0001", "req-0002", "req-0003"]
    for request_id in programmed_request_ids:
        fal_client.program_status(request_id, JobStatus(state="COMPLETED"))
        fal_client.program_result(
            request_id,
            {"images": [{"url": f"https://cdn.fal.local/{request_id}.png"}]},
        )
    downloader = FakeDownloader()

    monkeypatch.setenv("FALX_OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr(core, "default_fal_client", lambda: fal_client, raising=False)
    monkeypatch.setattr(io, "default_downloader", lambda: downloader, raising=False)

    result = CliRunner().invoke(
        app,
        ["run", "--config", str(config_path), "--iterations", "3", "--poll-interval", "0.01"],
    )

    assert result.exit_code == 0
    assert result.stdout.startswith("request_id:")
    assert not result.stdout.lstrip().startswith("{")
    payload = safe_load(result.stdout)
    takes_payload = payload["takes"]
    assert payload["status"] == "completed"
    assert payload["request_id"] in {take_["request_id"] for take_ in takes_payload}
    assert [take_["take"] for take_ in takes_payload] == [1, 2, 3]
    for take_payload in takes_payload:
        take_value = take_payload["take"]
        request_id = take_payload["request_id"]
        expected_path = (
            output_dir
            / f"v1-{take_value}"
            / f"G-0007_iter-many_v1-{take_value}-1.png"
        )
        assert take_payload["batches"] == [
            {"batch": 1, "file_path": str(expected_path)}
        ]
        assert request_id.startswith("req-")
    updated_input = safe_load(config_path.read_text(encoding="utf-8"))
    assert updated_input["parameters"]["image_urls"] == [
        "https://example.com/external.png",
        "https://cdn.fal.local/sample_asset.png",
    ]
    assert "uploads" not in updated_input
    assert "results" not in updated_input

    assert sorted(url for url, _ in downloader.downloads) == [
        "https://cdn.fal.local/req-0001.png",
        "https://cdn.fal.local/req-0002.png",
        "https://cdn.fal.local/req-0003.png",
    ]
