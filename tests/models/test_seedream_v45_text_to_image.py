from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SeedreamV45ImageSize, SeedreamV45TextToImageConfig


def test_seedream_v45_text_to_image_accepts_minimal_required_fields() -> None:
    config = SeedreamV45TextToImageConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/text-to-image",
        prompt="A crisp editorial photo of a ceramic vase on a lacquer table.",
    )

    assert config.prompt == "A crisp editorial photo of a ceramic vase on a lacquer table."
    assert config.image_size == SeedreamV45ImageSize(width=2048, height=2048)
    assert config.num_images == 1
    assert config.max_images == 1
    assert config.seed is None
    assert config.sync_mode is False
    assert config.enable_safety_checker is True


def test_seedream_v45_text_to_image_accepts_all_fields() -> None:
    config = SeedreamV45TextToImageConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/text-to-image",
        prompt="A bright product photo with clean typography.",
        image_size="auto_4K",
        num_images=6,
        max_images=6,
        seed=42,
        sync_mode=True,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
        "prompt": "A bright product photo with clean typography.",
        "image_size": "auto_4K",
        "num_images": 6,
        "max_images": 6,
        "seed": 42,
        "sync_mode": True,
        "enable_safety_checker": False,
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
def test_seedream_v45_text_to_image_accepts_image_size_presets(image_size: str) -> None:
    config = SeedreamV45TextToImageConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/text-to-image",
        prompt="A cinematic still life.",
        image_size=image_size,
    )

    assert config.image_size == image_size


def test_seedream_v45_text_to_image_accepts_custom_image_size_object() -> None:
    config = SeedreamV45TextToImageConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/text-to-image",
        prompt="A cinematic still life.",
        image_size={"width": 4096, "height": 4096},
    )

    assert config.image_size == SeedreamV45ImageSize(width=4096, height=4096)
    assert config.model_dump()["image_size"] == {"width": 4096, "height": 4096}


@pytest.mark.parametrize("value", [1, 6])
def test_seedream_v45_text_to_image_accepts_num_images_boundaries(value: int) -> None:
    config = SeedreamV45TextToImageConfig(
        app_id="fal-ai/bytedance/seedream/v4.5/text-to-image",
        prompt="A cinematic still life.",
        num_images=value,
        max_images=value,
    )

    assert config.num_images == value
    assert config.max_images == value


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image"}, "prompt"),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
                "prompt": "A cinematic still life.",
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
                "prompt": "A cinematic still life.",
                "image_size": "auto",
            },
            "image_size",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
                "prompt": "A cinematic still life.",
                "image_size": {"width": 0, "height": 2048},
            },
            "width",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
                "prompt": "A cinematic still life.",
                "image_size": {"width": 14143, "height": 2048},
            },
            "width",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
                "prompt": "A cinematic still life.",
                "num_images": 0,
            },
            "num_images",
        ),
        (
            {
                "app_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
                "prompt": "A cinematic still life.",
                "max_images": 7,
            },
            "max_images",
        ),
    ],
)
def test_seedream_v45_text_to_image_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SeedreamV45TextToImageConfig(**payload)
