from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import falx.core as core
import falx.io as io
from falx.cli import app
from tests.conftest import FakeDownloader, FakeFalClient, JobStatus
from tests.yaml_utils import safe_dump, safe_load

runner = CliRunner()


def _write_matrix_config(config_path: Path, *, output_dir: Path, version: int = 1) -> None:
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/text-to-video",
                "parameters": {"prompt": "placeholder", "aspect_ratio": "1:1"},
                "output_dir": str(output_dir),
                "slug": "matrix-demo",
                "version": version,
                "matrix_axes": {
                    "mode": "cartesian",
                    "axes": [{"field": "prompt", "values": ["A", "B"]}],
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _write_multi_field_matrix_config(
    config_path: Path,
    *,
    output_dir: Path,
    version: int = 1,
) -> None:
    config_path.write_text(
        safe_dump(
            {
                "app_id": "bytedance/seedance-2.0/text-to-video",
                "parameters": {
                    "prompt": "placeholder",
                    "aspect_ratio": "1:1",
                    "resolution": "480p",
                },
                "output_dir": str(output_dir),
                "slug": "matrix-demo",
                "version": version,
                "matrix_axes": {
                    "mode": "cartesian",
                    "axes": [
                        {
                            "fields": ["prompt", "aspect_ratio"],
                            "value_set": [["A", "16:9"], ["B", "1:1"]],
                        },
                        {"field": "resolution", "values": ["480p", "720p"]},
                    ],
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _install_fakes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    fal_client: FakeFalClient,
    downloader: Any | None = None,
) -> None:
    monkeypatch.setenv("FAL_KEY", "test-key")
    monkeypatch.setattr(core, "default_fal_client", lambda: fal_client, raising=False)
    if downloader is not None:
        monkeypatch.setattr(io, "default_downloader", lambda: downloader, raising=False)


def _program_completed(
    fal_client: FakeFalClient,
    request_id: str,
    url: str,
    file_name: str,
) -> None:
    fal_client.program_status(request_id, JobStatus(state="COMPLETED"))
    fal_client.program_result(
        request_id,
        {"video": {"url": url, "file_name": file_name}},
    )


def test_matrix_run_writes_canonical_compiled_children_and_completes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0008_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    _write_matrix_config(config_path, output_dir=output_dir)
    fal_client = FakeFalClient()
    for cell, request_id in [(1, "req-0001"), (2, "req-0002")]:
        _program_completed(
            fal_client,
            request_id,
            f"https://cdn.fal.local/cell-{cell}.mp4",
            f"cell-{cell}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    payload = safe_load(result.stdout)
    assert payload["matrix"] is True
    assert payload["status"] == "completed"
    assert [cell["cell"] for cell in payload["cells"]] == [1, 2]
    assert (output_dir / "c1-v1-1" / "G-0008_c1-v1-1-job.yaml").is_file()
    assert (output_dir / "c2-v1-1" / "G-0008_c2-v1-1-job.yaml").is_file()


def test_matrix_run_handles_multi_field_axis_cells(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0015_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    _write_multi_field_matrix_config(config_path, output_dir=output_dir)
    fal_client = FakeFalClient()
    for cell in range(1, 5):
        _program_completed(
            fal_client,
            f"req-{cell:04d}",
            f"https://cdn.fal.local/cell-{cell}.mp4",
            f"cell-{cell}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    payload = safe_load(result.stdout)
    assert [cell["cell"] for cell in payload["cells"]] == [1, 2, 3, 4]
    assert [cell["coords"] for cell in payload["cells"]] == [
        {"prompt": "A", "aspect_ratio": "16:9", "resolution": "480p"},
        {"prompt": "A", "aspect_ratio": "16:9", "resolution": "720p"},
        {"prompt": "B", "aspect_ratio": "1:1", "resolution": "480p"},
        {"prompt": "B", "aspect_ratio": "1:1", "resolution": "720p"},
    ]
    first_child = safe_load(
        (output_dir / "c1-v1-1" / "G-0015_c1-v1-1-job.yaml").read_text()
    )
    fourth_child = safe_load(
        (output_dir / "c4-v1-1" / "G-0015_c4-v1-1-job.yaml").read_text()
    )
    assert first_child["parameters"] == {
        "prompt": "A",
        "aspect_ratio": "16:9",
        "resolution": "480p",
    }
    assert fourth_child["parameters"] == {
        "prompt": "B",
        "aspect_ratio": "1:1",
        "resolution": "720p",
    }


def test_matrix_run_version_progression_writes_new_version_children(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0014_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    fal_client = FakeFalClient()
    for _cell, request_id in [(1, "req-0001"), (2, "req-0002"), (3, "req-0003"), (4, "req-0004")]:
        _program_completed(
            fal_client,
            request_id,
            f"https://cdn.fal.local/cell-{request_id}.mp4",
            f"cell-{request_id}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    _write_matrix_config(config_path, output_dir=output_dir, version=1)
    first = runner.invoke(app, ["run", "--config", str(config_path), "--poll-interval", "0"])
    assert first.exit_code == 0, first.stderr

    _write_matrix_config(config_path, output_dir=output_dir, version=2)
    second = runner.invoke(app, ["run", "--config", str(config_path), "--poll-interval", "0"])

    assert second.exit_code == 0, second.stderr
    assert (output_dir / "c1-v1-1" / "G-0014_c1-v1-1-job.yaml").is_file()
    assert (output_dir / "c2-v1-1" / "G-0014_c2-v1-1-job.yaml").is_file()
    assert (output_dir / "c1-v2-1" / "G-0014_c1-v2-1-job.yaml").is_file()
    assert (output_dir / "c2-v2-1" / "G-0014_c2-v2-1-job.yaml").is_file()
    assert not (output_dir / "c1-v2-2").exists()
    assert not (output_dir / "c2-v2-2").exists()


def test_matrix_run_downloads_files_into_cell_submit_folders(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0009_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    _write_matrix_config(config_path, output_dir=output_dir)
    fal_client = FakeFalClient()
    for request_id, cell in [("req-0001", 1), ("req-0002", 2)]:
        _program_completed(
            fal_client,
            request_id,
            f"https://cdn.fal.local/cell-{cell}.mp4",
            f"cell-{cell}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    cell1_path = output_dir / "c1-v1-1" / "G-0009_matrix-demo_c1_v1-1-1.mp4"
    cell2_path = output_dir / "c2-v1-1" / "G-0009_matrix-demo_c2_v1-1-1.mp4"
    payload = safe_load(result.stdout)
    assert payload["status"] == "completed"
    cells_by_id = {cell["cell"]: cell for cell in payload["cells"]}
    assert cells_by_id[1]["takes"][0]["batches"] == [
        {"batch": 1, "file_path": str(cell1_path)}
    ]
    assert cells_by_id[2]["takes"][0]["batches"] == [
        {"batch": 1, "file_path": str(cell2_path)}
    ]
    assert cells_by_id[1]["takes"][0]["take"] == 1
    assert cells_by_id[2]["takes"][0]["take"] == 1
    expected_downloads = sorted(
        [
            ("https://cdn.fal.local/cell-1.mp4", cell1_path),
            ("https://cdn.fal.local/cell-2.mp4", cell2_path),
        ]
    )
    assert sorted(downloader.downloads) == expected_downloads
    assert (output_dir / "c1-v1-1" / "G-0009_matrix-demo.yaml").is_file()
    assert (output_dir / "c2-v1-1" / "G-0009_matrix-demo.yaml").is_file()


def test_matrix_run_uses_next_take_after_completed_take_group(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0013_matrix-demo" / "output"
    for cell in (1, 2):
        completed_dir = output_dir / f"c{cell}-v1-1"
        completed_dir.mkdir(parents=True)
        (completed_dir / "out.mp4").write_bytes(b"completed")
    config_path = tmp_path / "matrix.yaml"
    _write_matrix_config(config_path, output_dir=output_dir)
    fal_client = FakeFalClient()
    for request_id, cell in [("req-0001", 1), ("req-0002", 2)]:
        _program_completed(
            fal_client,
            request_id,
            f"https://cdn.fal.local/cell-{cell}.mp4",
            f"cell-{cell}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    cell1_path = output_dir / "c1-v1-2" / "G-0013_matrix-demo_c1_v1-2-1.mp4"
    cell2_path = output_dir / "c2-v1-2" / "G-0013_matrix-demo_c2_v1-2-1.mp4"
    payload = safe_load(result.stdout)
    assert payload["status"] == "completed"
    cells_by_id = {cell["cell"]: cell for cell in payload["cells"]}
    assert cells_by_id[1]["takes"][0]["batches"] == [
        {"batch": 1, "file_path": str(cell1_path)}
    ]
    assert cells_by_id[2]["takes"][0]["batches"] == [
        {"batch": 1, "file_path": str(cell2_path)}
    ]
    assert cells_by_id[1]["takes"][0]["take"] == 2
    assert cells_by_id[2]["takes"][0]["take"] == 2


def _write_matrix_config_n_cells(
    config_path: Path,
    *,
    output_dir: Path,
    n_cells: int,
    max_concurrency: int | None = None,
) -> None:
    payload: dict[str, Any] = {
        "app_id": "bytedance/seedance-2.0/text-to-video",
        "parameters": {"prompt": "placeholder", "aspect_ratio": "1:1"},
        "output_dir": str(output_dir),
        "slug": "matrix-demo",
        "version": 1,
        "matrix_axes": {
            "mode": "cartesian",
            "axes": [{"field": "prompt", "values": [f"P{i}" for i in range(n_cells)]}],
        },
    }
    if max_concurrency is not None:
        payload["max_concurrency"] = max_concurrency
    config_path.write_text(safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_matrix_run_caps_in_flight_submits_at_max_concurrency(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """In-flight submits never exceed max_concurrency.

    A counting FakeFalClient tracks concurrent submits between `submit` entry
    and `status==COMPLETED` exit. With max_concurrency=2 and 6 cells, the peak
    concurrent in-flight count must not exceed 2.
    """
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0030_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    _write_matrix_config_n_cells(
        config_path, output_dir=output_dir, n_cells=6, max_concurrency=2
    )

    import asyncio

    class CountingClient(FakeFalClient):
        def __init__(self) -> None:
            super().__init__()
            self.in_flight = 0
            self.peak_in_flight = 0
            self.lock = asyncio.Lock()

        async def submit(
            self,
            app_id: str,
            arguments: dict[str, Any],
            *,
            headers: dict[str, str] | None = None,
        ) -> Any:
            async with self.lock:
                self.in_flight += 1
                self.peak_in_flight = max(self.peak_in_flight, self.in_flight)
            return await super().submit(app_id, arguments, headers=headers)

        async def status(self, app_id: str, request_id: str) -> Any:
            status = await super().status(app_id, request_id)
            if getattr(status, "state", None) == "COMPLETED":
                async with self.lock:
                    self.in_flight -= 1
            return status

    fal_client = CountingClient()
    for cell in range(1, 7):
        _program_completed(
            fal_client,
            f"req-{cell:04d}",
            f"https://cdn.fal.local/cell-{cell}.mp4",
            f"cell-{cell}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    assert fal_client.peak_in_flight <= 2


def test_matrix_run_one_cell_failure_does_not_block_other_cells(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Cell-level exception releases the semaphore so other cells still run.

    If submit raises for cell 1, cells 2 and 3 must still complete (= the
    semaphore was released via the `async with` context manager). The run
    reports failed because at least one cell failed, but other cells should
    have made it through the pipeline.
    """
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0031_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    _write_matrix_config_n_cells(config_path, output_dir=output_dir, n_cells=3)

    # Cell 1 will fail in the polling stage; cells 2 and 3 complete normally.
    fal_client = FakeFalClient()
    fal_client.program_status(
        "req-0001", JobStatus(state="COMPLETED", error="boom", error_type="server_error")
    )
    for cell in (2, 3):
        _program_completed(
            fal_client,
            f"req-{cell:04d}",
            f"https://cdn.fal.local/cell-{cell}.mp4",
            f"cell-{cell}.mp4",
        )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 2
    # cell 2 and 3 must have completed despite cell 1's failure.
    assert (output_dir / "c2-v1-1" / "G-0031_c2-v1-1-job.yaml").is_file()
    assert (output_dir / "c3-v1-1" / "G-0031_c3-v1-1-job.yaml").is_file()


def test_matrix_run_reports_skipped_cells_as_cell_objects(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0010_matrix-demo" / "output"
    config_path = tmp_path / "matrix.yaml"
    _write_matrix_config(config_path, output_dir=output_dir)
    completed_cell_dir = output_dir / "c2-v1-1"
    completed_cell_dir.mkdir(parents=True)
    (completed_cell_dir / "out.mp4").write_bytes(b"completed")
    fal_client = FakeFalClient()
    _program_completed(
        fal_client,
        "req-0001",
        "https://cdn.fal.local/cell-1.mp4",
        "cell-1.mp4",
    )
    downloader = FakeDownloader()
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    payload = safe_load(result.stdout)
    assert payload["status"] == "completed"
    assert [cell["cell"] for cell in payload["cells"]] == [1]
    assert payload.get("skipped_cells") == [{"cell": 2, "take": 1}]
