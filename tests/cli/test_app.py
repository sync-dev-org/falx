from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import falx.core as core
import falx.io as io
from falx.cli import app
from tests.conftest import FakeFalClient, FakeUploader, JobStatus
from tests.yaml_utils import safe_dump, safe_load

runner = CliRunner()


def _load_stdout_yaml(stdout: str) -> dict[str, Any]:
    assert stdout.startswith("request_id:")
    assert not stdout.lstrip().startswith("{")
    return safe_load(stdout)


def _write_config(
    path: Path,
    *,
    app_id: str = "fal-ai/flux/schnell",
    parameters: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    slug: str | None = "demo-cat",
    version: int = 1,
    iterations: int = 1,
) -> None:
    payload: dict[str, Any] = {
        "app_id": app_id,
        "parameters": parameters or {"prompt": "a cat sitting on a mat"},
        "iterations": iterations,
    }
    if output_dir is not None:
        payload["output_dir"] = str(output_dir)
    if slug is not None:
        payload["slug"] = slug
    payload["version"] = version
    path.write_text(safe_dump(payload, sort_keys=False), encoding="utf-8")


def _install_fakes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    fal_client: FakeFalClient,
    downloader: Any | None = None,
    uploader: FakeUploader | None = None,
) -> None:
    monkeypatch.setenv("FAL_KEY", "test-key")
    monkeypatch.setattr(core, "default_fal_client", lambda: fal_client, raising=False)
    if downloader is not None:
        monkeypatch.setattr(io, "default_downloader", lambda: downloader, raising=False)
    if uploader is not None:
        monkeypatch.setattr(io, "default_uploader", lambda: uploader, raising=False)


def test_fetch_requires_request_id(tmp_path: Path) -> None:
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=tmp_path / "output")

    result = runner.invoke(app, ["fetch", "--config", str(config_path)])

    assert result.exit_code == 2
    assert "Missing option '--request-id'" in result.stderr


def test_fetch_completed_request_downloads_files_and_prints_stdout_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0001_demo-cat" / "output"
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=output_dir, slug="demo-cat", version=2)
    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    fal_client.program_result(
        "req-0001",
        {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]},
    )
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        [
            "fetch",
            "--config",
            str(config_path),
            "--request-id",
            "req-0001",
            "--take",
            "3",
        ],
    )

    assert result.exit_code == 0, result.stderr
    payload = _load_stdout_yaml(result.stdout)
    expected_file = (
        output_dir
        / "v2-3"
        / "G-0001_demo-cat_v2-3-1.png"
    )
    assert payload == {
        "request_id": "req-0001",
        "status": "completed",
        "takes": [
            {
                "take": 3,
                "request_id": "req-0001",
                "batches": [{"batch": 1, "file_path": str(expected_file)}],
            }
        ],
    }
    assert downloader.downloads == [("https://fal.media/files/cat.png", expected_file)]


def test_fetch_uploads_local_url_paths_and_writes_single_result_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    asset_path = tmp_path / "local-image.png"
    asset_path.write_bytes(b"image payload")
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0002_fetch-demo" / "output"
    config_path = tmp_path / "job.yaml"
    _write_config(
        config_path,
        app_id="fal-ai/nano-banana-2/edit",
        parameters={"prompt": "use local reference", "image_urls": [str(asset_path)]},
        output_dir=output_dir,
        slug="fetch-demo",
        version=2,
    )
    request_id = "00000000-1111-2222-3333-4444deadbeef"
    fal_client = FakeFalClient()
    fal_client.program_status(request_id, JobStatus(state="COMPLETED"))
    raw_result = {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]}
    fal_client.program_result(request_id, raw_result)
    uploader = FakeUploader()
    _install_fakes(
        monkeypatch,
        fal_client=fal_client,
        downloader=downloader,
        uploader=uploader,
    )

    result = runner.invoke(
        app,
        [
            "fetch",
            "--config",
            str(config_path),
            "--request-id",
            request_id,
            "--take",
            "3",
        ],
    )

    assert result.exit_code == 0, result.stderr
    assert uploader.uploads == [asset_path.resolve()]
    payload = _load_stdout_yaml(result.stdout)
    expected_file = (
        output_dir
        / "v2-3"
        / "G-0002_fetch-demo_v2-3-1.png"
    )
    assert payload["takes"][0]["batches"] == [{"batch": 1, "file_path": str(expected_file)}]
    assert downloader.downloads == [("https://fal.media/files/cat.png", expected_file)]
    single_result_path = output_dir / "v2-3" / "G-0002_fetch-demo.yaml"
    single_result = safe_load(single_result_path.read_text())
    assert single_result["app_id"] == "fal-ai/nano-banana-2/edit"
    assert single_result["iterations"] == 1
    assert single_result["output_dir"] == str(output_dir)
    assert single_result["parameters"]["image_urls"] == ["https://cdn.fal.local/local-image.png"]
    assert "job_index" not in single_result["results"][0]
    assert single_result["results"][0]["request_id"] == request_id
    assert single_result["results"][0]["seed"] is None
    assert single_result["results"][0]["submitted_at"] is None
    assert isinstance(single_result["results"][0]["completed_at"], str)
    assert single_result["results"][0]["result"] == raw_result


def test_cancel_accepts_request_id_and_prints_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "job.yaml"
    _write_config(config_path)
    fal_client = FakeFalClient()
    _install_fakes(monkeypatch, fal_client=fal_client)

    result = runner.invoke(
        app,
        ["cancel", "--config", str(config_path), "--request-id", "req-0001"],
    )

    assert result.exit_code == 0, result.stderr
    assert _load_stdout_yaml(result.stdout) == {"request_id": "req-0001", "status": "cancelled"}
    assert fal_client.cancel_calls == [("fal-ai/flux/schnell", "req-0001")]


def test_run_completes_pipeline_and_prints_completed_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0003_demo-cat" / "output"
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=output_dir, slug="demo-cat")
    before = safe_load(config_path.read_text())
    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    fal_client.program_result(
        "req-0001",
        {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]},
    )
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    payload = _load_stdout_yaml(result.stdout)
    expected_file = (
        output_dir
        / "v1-1"
        / "G-0003_demo-cat_v1-1-1.png"
    )
    assert payload == {
        "request_id": "req-0001",
        "status": "completed",
        "takes": [
            {
                "take": 1,
                "request_id": "req-0001",
                "batches": [{"batch": 1, "file_path": str(expected_file)}],
            }
        ],
    }
    assert safe_load(config_path.read_text()) == before


def test_run_uses_next_take_across_existing_versions(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0011_demo-cat" / "output"
    (output_dir / "v1-1").mkdir(parents=True)
    (output_dir / "v1-1" / "old.png").write_bytes(b"old")
    (output_dir / "v1-2").mkdir()
    (output_dir / "v1-2" / "old.png").write_bytes(b"old")
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=output_dir, slug="demo-cat", version=2)
    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    fal_client.program_result(
        "req-0001",
        {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]},
    )
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    payload = _load_stdout_yaml(result.stdout)
    expected_file = output_dir / "v2-3" / "G-0011_demo-cat_v2-3-1.png"
    assert payload["takes"][0]["batches"] == [{"batch": 1, "file_path": str(expected_file)}]
    assert downloader.downloads == [("https://fal.media/files/cat.png", expected_file)]
    assert (output_dir / "v1-1" / "old.png").read_bytes() == b"old"
    assert (output_dir / "v1-2" / "old.png").read_bytes() == b"old"


def test_run_iterations_n_consumes_n_consecutive_takes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    """iterations=N で各 task が独立 take folder に着地し、disk 上で構造的に分離されること."""
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0012_demo-cat" / "output"
    (output_dir / "v1-1").mkdir(parents=True)
    (output_dir / "v1-1" / "old.png").write_bytes(b"old")
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=output_dir, slug="demo-cat", iterations=2)
    fal_client = FakeFalClient()
    for request_id in ("req-0001", "req-0002"):
        fal_client.program_status(request_id, JobStatus(state="COMPLETED"))
        fal_client.program_result(
            request_id,
            {"images": [{"url": f"https://fal.media/files/{request_id}.png"}]},
        )
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    payload = _load_stdout_yaml(result.stdout)
    take2_path = output_dir / "v1-2" / "G-0012_demo-cat_v1-2-1.png"
    take3_path = output_dir / "v1-3" / "G-0012_demo-cat_v1-3-1.png"
    assert payload == {
        "request_id": "req-0001",
        "status": "completed",
        "takes": [
            {
                "take": 2,
                "request_id": "req-0001",
                "batches": [{"batch": 1, "file_path": str(take2_path)}],
            },
            {
                "take": 3,
                "request_id": "req-0002",
                "batches": [{"batch": 1, "file_path": str(take3_path)}],
            },
        ],
    }
    assert sorted(downloader.downloads) == sorted(
        [
            ("https://fal.media/files/req-0001.png", take2_path),
            ("https://fal.media/files/req-0002.png", take3_path),
        ]
    )
    # Each task has its own take folder + single-result yaml, so the two takes
    # cannot overwrite each other.
    take2_yaml = safe_load(
        (output_dir / "v1-2" / "G-0012_demo-cat.yaml").read_text()
    )
    take3_yaml = safe_load(
        (output_dir / "v1-3" / "G-0012_demo-cat.yaml").read_text()
    )
    assert "job_index" not in take2_yaml["results"][0]
    assert "job_index" not in take3_yaml["results"][0]


def test_run_uploads_local_url_paths_and_writes_single_result_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    asset_path = tmp_path / "local-image.png"
    asset_path.write_bytes(b"image payload")
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0004_submit-demo" / "output"
    config_path = tmp_path / "job.yaml"
    _write_config(
        config_path,
        app_id="fal-ai/nano-banana-2/edit",
        parameters={"prompt": "use local reference", "image_urls": [str(asset_path)]},
        output_dir=output_dir,
        slug="submit-demo",
    )
    before = safe_load(config_path.read_text())
    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    raw_result = {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]}
    fal_client.program_result("req-0001", raw_result)
    uploader = FakeUploader()
    _install_fakes(
        monkeypatch,
        fal_client=fal_client,
        downloader=downloader,
        uploader=uploader,
    )

    result = runner.invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    assert uploader.uploads == [asset_path.resolve()]
    assert fal_client.submit_calls[0][1]["image_urls"] == ["https://cdn.fal.local/local-image.png"]
    payload = _load_stdout_yaml(result.stdout)
    expected_file = (
        output_dir
        / "v1-1"
        / "G-0004_submit-demo_v1-1-1.png"
    )
    assert payload["takes"][0]["batches"] == [{"batch": 1, "file_path": str(expected_file)}]
    assert downloader.downloads == [("https://fal.media/files/cat.png", expected_file)]
    assert safe_load(config_path.read_text()) == before
    single_result_path = output_dir / "v1-1" / "G-0004_submit-demo.yaml"
    single_result = safe_load(single_result_path.read_text())
    assert single_result["parameters"]["image_urls"] == ["https://cdn.fal.local/local-image.png"]
    assert "job_index" not in single_result["results"][0]
    assert single_result["results"][0]["request_id"] == "req-0001"
    assert single_result["results"][0]["seed"] == fal_client.submit_calls[0][1]["seed"]
    assert isinstance(single_result["results"][0]["submitted_at"], str)
    assert isinstance(single_result["results"][0]["completed_at"], str)
    assert single_result["results"][0]["result"] == raw_result


def test_submit_alias_emits_deprecation_warning_and_forwards_to_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0020_demo-cat" / "output"
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=output_dir, slug="demo-cat")
    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    fal_client.program_result(
        "req-0001",
        {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]},
    )
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["submit", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    assert "deprecated alias for `falx run`" in result.stderr
    payload = _load_stdout_yaml(result.stdout)
    expected_file = output_dir / "v1-1" / "G-0020_demo-cat_v1-1-1.png"
    assert payload["takes"][0]["batches"] == [
        {"batch": 1, "file_path": str(expected_file)}
    ]


def test_submit_async_alias_emits_deprecation_warning_and_forwards_to_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    downloader: Any,
) -> None:
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0021_demo-cat" / "output"
    config_path = tmp_path / "job.yaml"
    _write_config(config_path, output_dir=output_dir, slug="demo-cat")
    fal_client = FakeFalClient()
    fal_client.program_status("req-0001", JobStatus(state="COMPLETED"))
    fal_client.program_result(
        "req-0001",
        {"images": [{"url": "https://fal.media/files/cat.png", "file_name": "cat.png"}]},
    )
    _install_fakes(monkeypatch, fal_client=fal_client, downloader=downloader)

    result = runner.invoke(
        app,
        ["submit-async", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0, result.stderr
    assert "deprecated alias for `falx run`" in result.stderr
    payload = _load_stdout_yaml(result.stdout)
    expected_file = output_dir / "v1-1" / "G-0021_demo-cat_v1-1-1.png"
    assert payload["takes"][0]["batches"] == [
        {"batch": 1, "file_path": str(expected_file)}
    ]
