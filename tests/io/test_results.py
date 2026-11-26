from __future__ import annotations

from pathlib import Path
from typing import Any

from falx.io import place_result_files


def test_place_result_files_uses_canonical_submit_folder_and_filename_for_single_output(
    tmp_path: Path,
    downloader: Any,
) -> None:
    request_id = "019e39f9-cc47-7f61-abc0-353d92359304"
    result = {
        "image": {
            "url": "https://fal.media/files/smoke.jpg",
            "file_name": "smoke.jpg",
            "content_type": "image/jpeg",
        }
    }

    paths = place_result_files(
        result,
        output_dir=tmp_path / "workspace" / "demo" / "exp" / "G-0001_demo-cat" / "output",
        app_id="fal-ai/nano-banana-2",
        slug="demo-cat",
        version=2,
        take=3,
        request_id=request_id,
        downloader=downloader,
    )

    expected_path = (
        tmp_path
        / "workspace"
        / "demo"
        / "exp"
        / "G-0001_demo-cat"
        / "output"
        / "v2-3"
        / "G-0001_demo-cat_v2-3-1.jpg"
    )
    assert paths == [expected_path]
    assert downloader.downloads == [("https://fal.media/files/smoke.jpg", expected_path)]


def test_place_result_files_keeps_parallel_array_batch_indexes(
    tmp_path: Path,
    downloader: Any,
) -> None:
    request_id = "abcdefgh-1234-5678-90ab-cdef12345678"
    result = {
        "images": [
            {
                "url": "https://fal.media/files/smoke-1.png",
                "file_name": "smoke-1.png",
                "content_type": "image/png",
            },
            {
                "url": "https://fal.media/files/smoke-2.png",
                "file_name": "smoke-2.png",
                "content_type": "image/png",
            },
        ],
        "captions": [
            {
                "url": "https://fal.media/files/smoke-1.txt",
                "file_name": "smoke-1.txt",
                "content_type": "text/plain",
            },
            {
                "url": "https://fal.media/files/smoke-2.txt",
                "file_name": "smoke-2.txt",
                "content_type": "text/plain",
            },
        ],
        "has_nsfw_concepts": [False, False],
    }

    paths = place_result_files(
        result,
        output_dir=tmp_path / "workspace" / "demo" / "exp" / "G-0002_demo-cat" / "output",
        app_id="fal-ai/flux/schnell",
        slug="demo-cat",
        version=1,
        take=4,
        request_id=request_id,
        downloader=downloader,
    )

    assert [
        path.relative_to(tmp_path / "workspace" / "demo" / "exp" / "G-0002_demo-cat" / "output")
        for path in paths
    ] == [
        Path("v1-4/G-0002_demo-cat_v1-4-1.png"),
        Path("v1-4/G-0002_demo-cat_v1-4-1.txt"),
        Path("v1-4/G-0002_demo-cat_v1-4-2.png"),
        Path("v1-4/G-0002_demo-cat_v1-4-2.txt"),
    ]


def test_place_result_files_infers_extensions_from_filename_url_and_content_type(
    tmp_path: Path,
    downloader: Any,
) -> None:
    result = {
        "first": {
            "url": "https://fal.media/files/blob",
            "file_name": "named.png",
            "content_type": None,
        },
        "second": {
            "url": "https://fal.media/files/from-url.jpg?download=1",
            "content_type": None,
        },
        "third": {
            "url": "https://fal.media/files/no-extension",
            "content_type": "text/plain",
        },
    }

    paths = place_result_files(
        result,
        output_dir=tmp_path / "workspace" / "demo" / "exp" / "G-0003_demo-cat" / "output",
        app_id="fal-ai/flux/schnell",
        slug="demo-cat",
        version=1,
        take=1,
        request_id="abcdefgh-1234-5678-90ab-cdef12345678",
        downloader=downloader,
    )

    assert [
        path.relative_to(tmp_path / "workspace" / "demo" / "exp" / "G-0003_demo-cat" / "output")
        for path in paths
    ] == [
        Path("v1-1/G-0003_demo-cat_v1-1-1.png"),
        Path("v1-1/G-0003_demo-cat_v1-1-2.jpg"),
        Path("v1-1/G-0003_demo-cat_v1-1-3.txt"),
    ]


def test_place_result_files_coexists_with_pre_existing_legacy_named_folder(
    tmp_path: Path,
    downloader: Any,
) -> None:
    output_dir = tmp_path / "output"
    legacy_folder = output_dir / "fal-ai_nano-banana-2" / "01-2385633f"
    legacy_folder.mkdir(parents=True)
    legacy_artifact = legacy_folder / "legacy-keepsake.png"
    legacy_artifact.write_bytes(b"legacy payload from a prior naming era")

    request_id = "019e39f9-cc47-7f61-abc0-353d92359304"
    result = {
        "image": {
            "url": "https://fal.media/files/smoke.jpg",
            "file_name": "smoke.jpg",
            "content_type": "image/jpeg",
        }
    }

    paths = place_result_files(
        result,
        output_dir=output_dir,
        app_id="fal-ai/nano-banana-2",
        slug="demo-cat",
        version=4,
        take=1,
        request_id=request_id,
        downloader=downloader,
    )

    new_folder = output_dir / "v4-1"
    expected_new_path = new_folder / "demo-cat_v4-1-1.jpg"
    assert paths == [expected_new_path]
    assert legacy_folder.exists()
    assert legacy_artifact.read_bytes() == b"legacy payload from a prior naming era"
    assert new_folder.exists()
    assert new_folder != legacy_folder


def test_place_result_files_downloads_meshy_nested_file_objects(
    tmp_path: Path,
    downloader: Any,
) -> None:
    result = {
        "model_glb": {"url": "https://fal.media/files/model.glb"},
        "thumbnail": {"url": "https://fal.media/files/thumbnail.png"},
        "model_urls": {
            "fbx": {"url": "https://fal.media/files/model.fbx"},
            "obj": {"url": "https://fal.media/files/model.obj"},
            "usdz": {"url": "https://fal.media/files/model.usdz"},
            "stl": {"url": "https://fal.media/files/model.stl"},
            "blend": {"url": "https://fal.media/files/model.blend"},
            "glb": {"url": "https://fal.media/files/model.glb"},
        },
        "texture_urls": [
            {
                "base_color": {"url": "https://fal.media/files/base-color.png"},
                "metallic": {"url": "https://fal.media/files/metallic.png"},
                "normal": {"url": "https://fal.media/files/normal.png"},
                "roughness": {"url": "https://fal.media/files/roughness.png"},
            }
        ],
        "seed": 1234,
        "prompt": "treasure chest",
    }
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0001_chest" / "output"

    paths = place_result_files(
        result,
        output_dir=output_dir,
        app_id="meshy/v7/text-to-3d",
        slug="chest",
        version=1,
        take=1,
        request_id="abcdefgh-1234-5678-90ab-cdef12345678",
        downloader=downloader,
    )

    expected_paths = [
        output_dir / "v1-1/G-0001_chest_v1-1-1.glb",
        output_dir / "v1-1/G-0001_chest_v1-1-2.png",
        output_dir / "v1-1/G-0001_chest_v1-1-3_model_urls.fbx.fbx",
        output_dir / "v1-1/G-0001_chest_v1-1-3_model_urls.obj.obj",
        output_dir / "v1-1/G-0001_chest_v1-1-3_model_urls.usdz.usdz",
        output_dir / "v1-1/G-0001_chest_v1-1-3_model_urls.stl.stl",
        output_dir / "v1-1/G-0001_chest_v1-1-3_model_urls.blend.blend",
        output_dir / "v1-1/G-0001_chest_v1-1-3_model_urls.glb.glb",
        output_dir / "v1-1/G-0001_chest_v1-1-4_texture_urls.base_color.png",
        output_dir / "v1-1/G-0001_chest_v1-1-4_texture_urls.metallic.png",
        output_dir / "v1-1/G-0001_chest_v1-1-4_texture_urls.normal.png",
        output_dir / "v1-1/G-0001_chest_v1-1-4_texture_urls.roughness.png",
    ]
    expected_urls = [
        "https://fal.media/files/model.glb",
        "https://fal.media/files/thumbnail.png",
        "https://fal.media/files/model.fbx",
        "https://fal.media/files/model.obj",
        "https://fal.media/files/model.usdz",
        "https://fal.media/files/model.stl",
        "https://fal.media/files/model.blend",
        "https://fal.media/files/model.glb",
        "https://fal.media/files/base-color.png",
        "https://fal.media/files/metallic.png",
        "https://fal.media/files/normal.png",
        "https://fal.media/files/roughness.png",
    ]
    assert paths == expected_paths
    assert downloader.downloads == list(zip(expected_urls, expected_paths, strict=True))


def test_place_result_files_ignores_nested_dict_without_file_objects(
    tmp_path: Path,
    downloader: Any,
) -> None:
    paths = place_result_files(
        {"seed": 1, "meta": {"a": 1, "b": "x"}},
        output_dir=tmp_path / "output",
        app_id="meshy/v7/text-to-3d",
        slug="chest",
        version=1,
        take=1,
        request_id="abcdefgh-1234-5678-90ab-cdef12345678",
        downloader=downloader,
    )

    assert paths == []
    assert downloader.downloads == []


def test_place_result_files_ignores_non_file_values_within_nested_dict(
    tmp_path: Path,
    downloader: Any,
) -> None:
    result = {
        "model_urls": {
            "fbx": {"url": "https://fal.media/files/model.fbx"},
            "seed": 1234,
            "note": "generated model",
            "obj": {"url": "https://fal.media/files/model.obj"},
        },
        "thumbnail": {"url": "https://fal.media/files/thumbnail.png"},
    }
    output_dir = tmp_path / "output"

    paths = place_result_files(
        result,
        output_dir=output_dir,
        app_id="meshy/v7/text-to-3d",
        slug="chest",
        version=1,
        take=1,
        request_id="abcdefgh-1234-5678-90ab-cdef12345678",
        downloader=downloader,
    )

    expected_paths = [
        output_dir / "v1-1/chest_v1-1-1_model_urls.fbx.fbx",
        output_dir / "v1-1/chest_v1-1-1_model_urls.obj.obj",
        output_dir / "v1-1/chest_v1-1-2.png",
    ]
    assert paths == expected_paths
    assert downloader.downloads == [
        ("https://fal.media/files/model.fbx", expected_paths[0]),
        ("https://fal.media/files/model.obj", expected_paths[1]),
        ("https://fal.media/files/thumbnail.png", expected_paths[2]),
    ]


def test_place_result_files_ignores_file_objects_beyond_one_nested_level(
    tmp_path: Path,
    downloader: Any,
) -> None:
    paths = place_result_files(
        {
            "model_urls": {
                "archive": {
                    "fbx": {"url": "https://fal.media/files/model.fbx"},
                }
            }
        },
        output_dir=tmp_path / "output",
        app_id="meshy/v7/text-to-3d",
        slug="chest",
        version=1,
        take=1,
        request_id="abcdefgh-1234-5678-90ab-cdef12345678",
        downloader=downloader,
    )

    assert paths == []
    assert downloader.downloads == []
