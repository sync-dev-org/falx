from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from typer.testing import CliRunner

import falx.core as core
import falx.io as io
from falx.cli import app
from tests.conftest import FakeFalClient, JobStatus
from tests.yaml_utils import safe_dump


class ImageDownloader:
    def __init__(self, images: dict[str, np.ndarray]) -> None:
        self.images = images

    def download(self, url: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.suffix.lower() == ".mp4":
            dest.write_bytes(b"fake-video")
            return
        image = self.images[url]
        ok = cv2.imwrite(str(dest), image)
        assert ok


def _write_config(
    path: Path,
    *,
    output_dir: Path,
    num_images: int,
    iterations: int = 1,
) -> None:
    path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/nano-banana-2",
                "parameters": {
                    "prompt": "contact sheet test",
                    "num_images": num_images,
                    "output_format": "png",
                },
                "output_dir": str(output_dir),
                "slug": "contact-sheet-test",
                "version": 1,
                "iterations": iterations,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _solid_images(count: int, *, width: int, height: int) -> dict[str, np.ndarray]:
    images: dict[str, np.ndarray] = {}
    for index in range(count):
        color = (
            40 + index * 30,
            90 + index * 20,
            150 + index * 10,
        )
        images[f"https://cdn.fal.local/image-{index}.png"] = np.full(
            (height, width, 3),
            color,
            dtype=np.uint8,
        )
    return images


def _install_run_fakes(
    monkeypatch,
    *,
    fal_client: FakeFalClient,
    downloader: ImageDownloader,
) -> None:
    monkeypatch.setenv("FAL_KEY", "test-key")
    monkeypatch.setattr(core, "default_fal_client", lambda: fal_client, raising=False)
    monkeypatch.setattr(io, "default_downloader", lambda: downloader, raising=False)


def _program_completed_result(
    fal_client: FakeFalClient,
    request_id: str,
    urls: list[str],
) -> None:
    fal_client.program_status(request_id, JobStatus(state="COMPLETED"))
    fal_client.program_result(
        request_id,
        {"images": [{"url": url} for url in urls]},
    )


def _read_single_thumbnail(output_dir: Path) -> tuple[Path, np.ndarray]:
    [thumbnail_path] = output_dir.rglob("*_contact.jpg")
    thumbnail = cv2.imread(str(thumbnail_path), cv2.IMREAD_COLOR)
    assert thumbnail is not None
    return thumbnail_path, thumbnail


def _expected_contact_sheet_bytes(
    tmp_path: Path,
    images: list[np.ndarray],
    *,
    cols: int,
    rows: int,
) -> bytes:
    first = images[0]
    scale = 0.5
    cell_size = (round(first.shape[1] * scale), round(first.shape[0] * scale))
    canvas = np.zeros((cell_size[1] * rows, cell_size[0] * cols, 3), dtype=np.uint8)
    for index, image in enumerate(images):
        resized = cv2.resize(image, cell_size, interpolation=cv2.INTER_AREA)
        row, col = divmod(index, cols)
        y = row * cell_size[1]
        x = col * cell_size[0]
        canvas[y : y + cell_size[1], x : x + cell_size[0]] = resized

    expected_path = tmp_path / "expected.jpg"
    ok = cv2.imwrite(
        str(expected_path),
        canvas,
        [int(cv2.IMWRITE_JPEG_QUALITY), 90],
    )
    assert ok
    return expected_path.read_bytes()


def test_run_writes_four_image_contact_sheet_as_2x2_without_padding(
    monkeypatch,
    tmp_path: Path,
) -> None:
    output_dir = (
        tmp_path / "workspace" / "demo" / "exp" / "G-0005_contact-sheet-test" / "output"
    )
    config_path = tmp_path / "four.yaml"
    _write_config(config_path, output_dir=output_dir, num_images=4)
    source_images = _solid_images(4, width=320, height=160)
    fal_client = FakeFalClient()
    _program_completed_result(fal_client, "req-0001", list(source_images))
    _install_run_fakes(
        monkeypatch,
        fal_client=fal_client,
        downloader=ImageDownloader(source_images),
    )

    result = CliRunner().invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0
    thumbnail_path, thumbnail = _read_single_thumbnail(output_dir)
    assert thumbnail_path.parent == output_dir / "v1-1"
    assert thumbnail_path.name == "G-0005_contact-sheet-test_v1-1_contact.jpg"
    assert thumbnail.shape == (160, 320, 3)
    assert thumbnail[40, 80].mean() > 20
    assert thumbnail[40, 240].mean() > 20
    assert thumbnail[120, 80].mean() > 20
    assert thumbnail[120, 240].mean() > 20
    assert thumbnail_path.read_bytes() == _expected_contact_sheet_bytes(
        tmp_path,
        list(source_images.values()),
        cols=2,
        rows=2,
    )


def test_run_writes_five_image_contact_sheet_as_3x2_with_black_padding(
    tmp_path: Path,
) -> None:
    source_images = _solid_images(5, width=160, height=320)
    source_paths: list[Path] = []
    for index, image in enumerate(source_images.values()):
        path = tmp_path / f"source-{index}.png"
        ok = cv2.imwrite(str(path), image)
        assert ok
        source_paths.append(path)

    thumbnail_path = io.write_contact_sheet_thumbnail(
        source_paths,
        destination=tmp_path / "five_contact.jpg",
    )

    thumbnail = cv2.imread(str(thumbnail_path), cv2.IMREAD_COLOR)
    assert thumbnail is not None
    assert thumbnail.shape == (320, 240, 3)
    padding_cell = thumbnail[160:320, 160:240]
    assert padding_cell[16:-16, 16:-16].max() == 0


def test_run_does_not_write_thumbnail_when_num_images_is_one(
    monkeypatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "outputs"
    config_path = tmp_path / "single.yaml"
    _write_config(config_path, output_dir=output_dir, num_images=1)
    source_images = _solid_images(1, width=160, height=160)
    fal_client = FakeFalClient()
    _program_completed_result(fal_client, "req-0001", list(source_images))
    _install_run_fakes(
        monkeypatch,
        fal_client=fal_client,
        downloader=ImageDownloader(source_images),
    )

    result = CliRunner().invoke(
        app,
        ["run", "--config", str(config_path), "--poll-interval", "0"],
    )

    assert result.exit_code == 0
    assert list(output_dir.rglob("*_contact.jpg")) == []


def test_run_skips_all_thumbnails_when_any_video_output_is_present(
    monkeypatch,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "outputs"
    config_path = tmp_path / "mixed.yaml"
    _write_config(config_path, output_dir=output_dir, num_images=2, iterations=2)
    source_images = _solid_images(2, width=160, height=160)
    fal_client = FakeFalClient()
    _program_completed_result(fal_client, "req-0001", list(source_images))
    _program_completed_result(
        fal_client,
        "req-0002",
        ["https://cdn.fal.local/video.mp4"],
    )
    _install_run_fakes(
        monkeypatch,
        fal_client=fal_client,
        downloader=ImageDownloader(source_images),
    )

    result = CliRunner().invoke(
        app,
        ["submit", "--config", str(config_path), "--iterations", "2", "--poll-interval", "0"],
    )

    assert result.exit_code == 0
    assert list(output_dir.rglob("*_contact.jpg")) == []
