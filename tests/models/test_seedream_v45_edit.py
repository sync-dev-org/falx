from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SeedreamV45EditConfig, SeedreamV45ImageSize


def test_seedream_v45_edit_accepts_minimal_required_fields() -> None:
    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Replace the product in Figure 1 with that in Figure 2.",
        image_urls=["https://example.com/input.png"],
    )

    assert config.prompt == "Replace the product in Figure 1 with that in Figure 2."
    assert config.image_urls == ["https://example.com/input.png"]
    assert config.image_size == SeedreamV45ImageSize(width=2048, height=2048)
    assert config.num_images == 1
    assert config.max_images == 1
    assert config.seed is None
    assert config.sync_mode is False
    assert config.enable_safety_checker is True


def test_seedream_v45_edit_accepts_all_fields() -> None:
    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Make the first image use the packaging shown in the second image.",
        image_urls=["https://example.com/source.png", "./fixtures/product.png"],
        image_size="auto_4K",
        num_images=2,
        max_images=4,
        seed=42,
        sync_mode=True,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
        "prompt": "Make the first image use the packaging shown in the second image.",
        "image_size": "auto_4K",
        "num_images": 2,
        "max_images": 4,
        "seed": 42,
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
        "auto_4K",
    ],
)
def test_seedream_v45_edit_accepts_image_size_presets(image_size: str) -> None:
    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Make the scene warmer.",
        image_urls=["https://example.com/input.png"],
        image_size=image_size,
    )

    assert config.image_size == image_size


def test_seedream_v45_edit_accepts_custom_image_size_object() -> None:
    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Make the scene warmer.",
        image_urls=["https://example.com/input.png"],
        image_size={"width": 4096, "height": 4096},
    )

    assert config.image_size == SeedreamV45ImageSize(width=4096, height=4096)
    assert config.model_dump()["image_size"] == {"width": 4096, "height": 4096}


def test_seedream_v45_edit_accepts_ten_input_images() -> None:
    image_urls = [f"https://example.com/input-{index}.png" for index in range(10)]

    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Use all ten references.",
        image_urls=image_urls,
    )

    assert config.image_urls == image_urls


@pytest.mark.parametrize("image_count", [0, 11])
def test_seedream_v45_edit_preserves_reference_array_without_item_limits(image_count: int) -> None:
    image_urls = [f"https://example.com/input-{index}.png" for index in range(image_count)]

    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Use the endpoint's last-ten behavior.",
        image_urls=image_urls,
    )

    assert config.model_dump(exclude={"app_id"})["image_urls"] == image_urls
    schema = SeedreamV45EditConfig.model_json_schema()
    assert "image_urls" in schema["required"]
    assert schema["properties"]["image_urls"]["items"] == {"type": "string"}
    assert "minItems" not in schema["properties"]["image_urls"]
    assert "maxItems" not in schema["properties"]["image_urls"]


@pytest.mark.parametrize(
    ("image_count", "num_images", "max_images"),
    [
        (9, 1, 6),
        (3, 2, 6),
        (10, 1, 5),
    ],
)
def test_seedream_v45_edit_accepts_total_input_and_output_image_limit(
    image_count: int,
    num_images: int,
    max_images: int,
) -> None:
    config = SeedreamV45EditConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/edit",
        prompt="Keep the composition and revise the product.",
        image_urls=[f"https://example.com/input-{index}.png" for index in range(image_count)],
        num_images=num_images,
        max_images=max_images,
    )

    assert len(config.image_urls) + config.num_images * config.max_images == 15


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "fal-ai/bytedance/seedream/v4.5/edit"}, "prompt"),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
                "prompt": "Make the scene warmer.",
            },
            "image_urls",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "image_size": "auto",
            },
            "image_size",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "num_images": 7,
            },
            "num_images",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": [f"https://example.com/input-{index}.png" for index in range(10)],
                "num_images": 1,
                "max_images": 6,
            },
            "total number of images",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/edit",
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "image_size": {"width": 2048, "height": 2048, "unit": "px"},
            },
            "unit",
        ),
    ],
)
def test_seedream_v45_edit_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SeedreamV45EditConfig(**payload)
