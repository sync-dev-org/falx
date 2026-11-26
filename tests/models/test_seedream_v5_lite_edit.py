from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SeedreamV5LiteEditConfig, SeedreamV5LiteImageSize


def test_seedream_v5_lite_edit_accepts_minimal_required_fields() -> None:
    config = SeedreamV5LiteEditConfig(
        app_id="fal-ai/bytedance/seedream/v5/lite/edit",
        prompt="Replace the product in Figure 1 with that in Figure 2.",
        image_urls=["https://example.com/input.png"],
    )

    assert config.prompt == "Replace the product in Figure 1 with that in Figure 2."
    assert config.image_urls == ["https://example.com/input.png"]
    assert config.image_size == "auto_2K"
    assert config.num_images == 1
    assert config.max_images == 1
    assert config.sync_mode is False
    assert config.enable_safety_checker is True


def test_seedream_v5_lite_edit_accepts_all_fields() -> None:
    config = SeedreamV5LiteEditConfig(
        app_id="fal-ai/bytedance/seedream/v5/lite/edit",
        prompt="Make the first image use the packaging shown in the second image.",
        image_urls=["https://example.com/source.png", "./fixtures/product.png"],
        image_size="auto_3K",
        num_images=6,
        max_images=6,
        sync_mode=True,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
        "prompt": "Make the first image use the packaging shown in the second image.",
        "image_size": "auto_3K",
        "num_images": 6,
        "max_images": 6,
        "sync_mode": True,
        "enable_safety_checker": False,
        "image_urls": [
            "https://example.com/source.png",
            "./fixtures/product.png",
        ],
    }


@pytest.mark.parametrize(
    "image_size",
    [
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
        "auto_2K",
        "auto_3K",
        "auto_4K",
    ],
)
def test_seedream_v5_lite_edit_accepts_image_size_presets(image_size: str) -> None:
    config = SeedreamV5LiteEditConfig(
        app_id="fal-ai/bytedance/seedream/v5/lite/edit",
        prompt="Make the scene warmer.",
        image_urls=["https://example.com/input.png"],
        image_size=image_size,
    )

    assert config.image_size == image_size


def test_seedream_v5_lite_edit_accepts_custom_image_size_object() -> None:
    config = SeedreamV5LiteEditConfig(
        app_id="fal-ai/bytedance/seedream/v5/lite/edit",
        prompt="Make the scene warmer.",
        image_urls=["https://example.com/input.png"],
        image_size={"width": 3072, "height": 3072},
    )

    assert config.image_size == SeedreamV5LiteImageSize(width=3072, height=3072)
    assert config.model_dump()["image_size"] == {"width": 3072, "height": 3072}


def test_seedream_v5_lite_edit_accepts_ten_input_images() -> None:
    image_urls = [f"https://example.com/input-{index}.png" for index in range(10)]

    config = SeedreamV5LiteEditConfig(
        app_id="fal-ai/bytedance/seedream/v5/lite/edit",
        prompt="Use all ten references.",
        image_urls=image_urls,
    )

    assert config.image_urls == image_urls


def test_seedream_v5_lite_edit_rejects_more_than_ten_input_images() -> None:
    image_urls = [f"https://example.com/input-{index}.png" for index in range(11)]

    with pytest.raises(ValidationError, match="image_urls"):
        SeedreamV5LiteEditConfig(
            app_id="fal-ai/bytedance/seedream/v5/lite/edit",
            prompt="Use all references.",
            image_urls=image_urls,
        )


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "fal-ai/bytedance/seedream/v5/lite/edit"}, "prompt"),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
            },
            "image_urls",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": [],
            },
            "image_urls",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "image_size": "auto",
            },
            "image_size",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "num_images": 7,
            },
            "num_images",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "return_byteplus_urls": True,
            },
            "return_byteplus_urls",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "seed": 42,
            },
            "seed",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v5/lite/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "image_size": {"width": 2048, "height": 2048, "unit": "px"},
            },
            "unit",
        ),
    ],
)
def test_seedream_v5_lite_edit_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SeedreamV5LiteEditConfig(**payload)
