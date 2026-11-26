from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass, field
from pathlib import Path

import fal_client
import pytest

import falx.core as core
import falx.io as io
from falx.io import default_uploader, upload_file_to_cdn, validate_job_config
from falx.models import JobConfig


@dataclass
class RecordingUploader:
    urls: list[str] = field(default_factory=list)
    calls: list[Path] = field(default_factory=list)

    def upload(self, path: Path) -> str:
        self.calls.append(Path(path))
        if self.urls:
            return self.urls.pop(0)
        return f"https://cdn.fal.local/{Path(path).name}"


@dataclass
class PayloadRecordingUploader:
    calls: list[Path] = field(default_factory=list)
    payloads: list[bytes] = field(default_factory=list)

    def upload(self, path: Path) -> str:
        self.calls.append(Path(path))
        self.payloads.append(Path(path).read_bytes())
        return f"https://cdn.fal.local/{Path(path).name}"


@pytest.mark.parametrize(
    ("stem", "expected"),
    [
        ("red_apple", "red_apple"),
        ("red apple", "red-apple"),
        ("red-apple", "red-apple"),
        ("my-awesome_file!", "my-awesome_file"),
        ("asset.with.dots", "asset.with.dots"),
        ("赤林檎", "akabayashigo"),
        ("赤りんご_v2", "akaringo_v2"),
        ("リンゴ", "ringo"),
        ("apple林檎", "appleringo"),
        ("龙猫", f"asset-{hashlib.sha256('龙猫'.encode()).hexdigest()[:8]}"),
        ("", f"asset-{hashlib.sha256(b'').hexdigest()[:8]}"),
        ("!!!", f"asset-{hashlib.sha256(b'!!!').hexdigest()[:8]}"),
        ("red!!!apple", "red-apple"),
    ],
)
def test_ascii_slugify_normalizes_stems(stem: str, expected: str) -> None:
    assert io._ascii_slugify(stem) == expected


def test_upload_file_to_cdn_uploads_ascii_slug_match_without_temp_copy(tmp_path: Path) -> None:
    local_path = tmp_path / "red_apple.png"
    local_path.write_bytes(b"same path")
    uploader = PayloadRecordingUploader()

    url = upload_file_to_cdn(local_path, uploader)

    assert url == "https://cdn.fal.local/red_apple.png"
    assert uploader.calls == [local_path.resolve()]
    assert uploader.payloads == [b"same path"]


def test_upload_file_to_cdn_uploads_ascii_slug_copy_with_same_payload(tmp_path: Path) -> None:
    local_path = tmp_path / "red apple.png"
    local_path.write_bytes(b"slugged payload")
    uploader = PayloadRecordingUploader()

    url = upload_file_to_cdn(local_path, uploader)

    assert url == "https://cdn.fal.local/red-apple.png"
    assert uploader.calls[0].name == "red-apple.png"
    assert not uploader.calls[0].exists()
    assert uploader.payloads == [b"slugged payload"]


def test_upload_file_to_cdn_uploads_non_ascii_slug_copy(tmp_path: Path) -> None:
    local_path = tmp_path / "赤林檎.png"
    local_path.write_bytes(b"red apple payload")
    uploader = PayloadRecordingUploader()

    url = upload_file_to_cdn(local_path, uploader)

    assert url == "https://cdn.fal.local/akabayashigo.png"
    assert uploader.calls[0].name == "akabayashigo.png"
    assert not uploader.calls[0].exists()
    assert uploader.payloads == [b"red apple payload"]


def test_upload_file_to_cdn_replaces_non_ascii_suffix_with_bin(tmp_path: Path) -> None:
    local_path = tmp_path / "asset.画像"
    local_path.write_bytes(b"payload")
    uploader = PayloadRecordingUploader()

    url = upload_file_to_cdn(local_path, uploader)

    assert url == "https://cdn.fal.local/asset.bin"
    assert uploader.calls[0].name == "asset.bin"
    assert uploader.payloads == [b"payload"]


def test_upload_file_to_cdn_raises_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.png"
    uploader = RecordingUploader()

    with pytest.raises(FileNotFoundError):
        upload_file_to_cdn(missing, uploader)

    assert uploader.calls == []


def test_validate_job_config_accepts_local_path_in_url_field(tmp_path: Path) -> None:
    local_path = tmp_path / "image.png"
    local_path.write_bytes(b"payload")
    config = JobConfig(
        app_id="bytedance/seedance-2.0/image-to-video",
        parameters={"prompt": "local file", "image_url": str(local_path)},
        slug="demo-cat",
        version=1,
    )

    validate_job_config(config)


def test_validate_job_config_rejects_missing_local_path_in_url_field(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.png"
    config = JobConfig(
        app_id="bytedance/seedance-2.0/image-to-video",
        parameters={"prompt": "missing file", "image_url": str(missing_path)},
        slug="demo-cat",
        version=1,
    )

    with pytest.raises(ValueError, match="public URL or local file path"):
        validate_job_config(config)


def test_validate_job_config_accepts_none_in_url_field() -> None:
    config = JobConfig(
        app_id="fal-ai/vidu/q3/image-to-video",
        parameters={
            "prompt": "empty optional field",
            "image_url": "https://example.com/source.png",
            "end_image_url": None,
        },
        slug="demo-cat",
        version=1,
    )

    validate_job_config(config)


def test_validate_job_config_resolves_project_root_relative_path_via_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asset_dir = tmp_path / "workspace" / "demo-project" / "exp" / "G-0001_demo" / "assets"
    asset_dir.mkdir(parents=True)
    asset_path = asset_dir / "image.png"
    asset_path.write_bytes(b"payload")
    relative_path = "workspace/demo-project/exp/G-0001_demo/assets/image.png"
    config = JobConfig(
        app_id="bytedance/seedance-2.0/image-to-video",
        parameters={"prompt": "project root relative", "image_url": relative_path},
        slug="demo-cat",
        version=1,
    )

    monkeypatch.chdir(tmp_path)
    validate_job_config(config)


def test_validate_job_config_rejects_relative_path_when_not_resolvable_from_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    asset_path = other_dir / "image.png"
    asset_path.write_bytes(b"payload")
    config = JobConfig(
        app_id="bytedance/seedance-2.0/image-to-video",
        parameters={"prompt": "relative not in cwd", "image_url": "image.png"},
        slug="demo-cat",
        version=1,
    )

    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="public URL or local file path"):
        validate_job_config(config)


def test_validate_job_config_signature_does_not_accept_base_dir() -> None:
    parameters = inspect.signature(validate_job_config).parameters
    assert "base_dir" not in parameters


def test_validate_job_config_accepts_public_url_in_url_field() -> None:
    config = JobConfig(
        app_id="bytedance/seedance-2.0/image-to-video",
        parameters={
            "prompt": "public url",
            "image_url": "https://example.com/image.png",
        },
        slug="demo-cat",
        version=1,
    )

    validate_job_config(config)


def test_default_uploader_calls_fal_client_upload_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.png"
    path.write_bytes(b"fake")
    calls: list[Path] = []

    monkeypatch.setenv("FAL_KEY", "key")
    monkeypatch.setattr(core, "ensure_fal_key", lambda: None)

    def fake_upload_file(upload_path: Path) -> str:
        calls.append(upload_path)
        return "https://cdn.fal.local/sample.png"

    monkeypatch.setattr(fal_client, "upload_file", fake_upload_file)

    assert default_uploader().upload(path) == "https://cdn.fal.local/sample.png"
    assert calls == [path]
