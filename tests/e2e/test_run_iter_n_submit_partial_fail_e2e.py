from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import falx.core as core
import falx.io as io
from falx.cli import app
from falx.core import SubmitHandle
from tests.conftest import FakeDownloader, FakeFalClient, JobStatus
from tests.yaml_utils import safe_dump, safe_load


class _FakeHTTPError(RuntimeError):
    """submit 段で raise する simulated HTTPError (= 422 content_policy_violation 相当)."""


def test_run_iter_n_submit_partial_fail_normalizes_stdout(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """submit に失敗した task があっても、他の task は完走する。

    CLI は exit 2 と status: failed の stdout YAML を返し、takes[] に成功した
    task と失敗した task の両方を含める。
    """
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0007_partial" / "output"
    config_path = tmp_path / "iter-partial.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/nano-banana-2/edit",
                "parameters": {
                    "prompt": "partial fail test",
                    "image_urls": ["https://example.com/external.png"],
                },
                "slug": "iter-partial",
                "version": 1,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    fal_client = FakeFalClient()
    call_count = {"n": 0}

    def submit_callable(
        app_id: str,
        arguments: dict,
        headers: dict | None,
    ) -> SubmitHandle:
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise _FakeHTTPError("partner_validation_failed simulated")
        rid = f"req-{call_count['n']:04d}"
        base = f"https://queue.fal.run/{app_id}/requests/{rid}"
        return SubmitHandle(
            request_id=rid,
            response_url=base,
            status_url=base + "/status",
            cancel_url=base + "/cancel",
        )

    fal_client.program_submit(submit_callable)
    for rid in ("req-0001", "req-0003"):
        fal_client.program_status(rid, JobStatus(state="COMPLETED"))
        fal_client.program_result(
            rid, {"images": [{"url": f"https://cdn.fal.local/{rid}.png"}]}
        )
    downloader = FakeDownloader()

    monkeypatch.setenv("FALX_OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr(core, "default_fal_client", lambda: fal_client, raising=False)
    monkeypatch.setattr(io, "default_downloader", lambda: downloader, raising=False)

    result = CliRunner().invoke(
        app,
        ["run", "--config", str(config_path), "--iterations", "3", "--poll-interval", "0.01"],
    )

    assert result.exit_code == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    payload = safe_load(result.stdout)
    assert payload["status"] == "failed"
    takes = payload["takes"]
    assert len(takes) == 3

    success_takes = [t for t in takes if t.get("batches")]
    failure_takes = [t for t in takes if not t.get("batches")]
    assert len(success_takes) == 2, f"takes: {takes}"
    assert len(failure_takes) == 1, f"takes: {takes}"

    failure = failure_takes[0]
    assert failure.get("error"), f"failure take must carry error: {failure}"
    assert failure.get("error_type") == "_FakeHTTPError"

    success_rids = {t["request_id"] for t in success_takes}
    assert success_rids == {"req-0001", "req-0003"}, f"got {success_rids}"
