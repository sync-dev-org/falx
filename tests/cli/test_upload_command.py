from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import falx.cli as cli
import falx.io as io

runner = CliRunner()


class RecordingUploader:
    def __init__(self, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.calls: list[Path] = []

    def upload(self, path: Path) -> str:
        self.calls.append(Path(path))
        if self.fail_on is not None and Path(path).name == self.fail_on:
            raise RuntimeError("upload failed")
        return f"https://cdn.fal.local/{Path(path).name}"


def test_upload_prints_original_path_and_slugged_cdn_url(
    monkeypatch,
    tmp_path: Path,
) -> None:
    asset = tmp_path / "赤りんご.png"
    asset.write_bytes(b"payload")
    uploader = RecordingUploader()
    monkeypatch.setattr(io, "default_uploader", lambda: uploader, raising=False)

    result = runner.invoke(cli.app, ["upload", str(asset)])

    assert result.exit_code == 0
    assert result.stdout == f"{asset}\thttps://cdn.fal.local/akaringo.png\n"
    assert uploader.calls[0].name == "akaringo.png"
    assert not uploader.calls[0].exists()


def test_upload_exits_one_on_partial_failure_and_keeps_success_stdout(
    monkeypatch,
    tmp_path: Path,
) -> None:
    ok = tmp_path / "ok.png"
    broken = tmp_path / "broken.png"
    ok.write_bytes(b"ok")
    broken.write_bytes(b"broken")
    uploader = RecordingUploader(fail_on="broken.png")
    monkeypatch.setattr(io, "default_uploader", lambda: uploader, raising=False)

    result = runner.invoke(cli.app, ["upload", str(ok), str(broken)])

    assert result.exit_code == 1
    assert result.stdout == f"{ok}\thttps://cdn.fal.local/ok.png\n"
    assert str(broken) in result.stderr
    assert "upload failed" in result.stderr
