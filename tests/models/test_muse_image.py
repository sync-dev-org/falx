from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    MuseImageTextToImageConfig,
    config_class_for_app_id,
)

APP_ID = "meta/muse-image/text-to-image"
ASPECT_RATIOS = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]


def test_muse_image_text_to_image_accepts_schema_defaults() -> None:
    config = MuseImageTextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic editorial portrait.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A cinematic editorial portrait.",
        "aspect_ratio": None,
        "num_images": 1,
        "output_format": "webp",
        "sync_mode": False,
    }


def test_muse_image_text_to_image_accepts_all_fields() -> None:
    config = MuseImageTextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic editorial portrait.",
        aspect_ratio="21:9",
        num_images=10,
        output_format="png",
        sync_mode=True,
    )

    assert config.aspect_ratio == "21:9"
    assert config.num_images == 10
    assert config.output_format == "png"
    assert config.sync_mode is True


@pytest.mark.parametrize("aspect_ratio", [None, *ASPECT_RATIOS])
def test_muse_image_text_to_image_accepts_nullable_aspect_ratio_enum(
    aspect_ratio: str | None,
) -> None:
    config = MuseImageTextToImageConfig(
        app_id=APP_ID,
        prompt="A portrait.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("num_images", [1, 10])
def test_muse_image_text_to_image_accepts_num_images_boundaries(num_images: int) -> None:
    config = MuseImageTextToImageConfig(
        app_id=APP_ID,
        prompt="A portrait.",
        num_images=num_images,
    )

    assert config.num_images == num_images


@pytest.mark.parametrize("output_format", ["jpeg", "png", "webp"])
def test_muse_image_text_to_image_accepts_output_format_enum(output_format: str) -> None:
    config = MuseImageTextToImageConfig(
        app_id=APP_ID,
        prompt="A portrait.",
        output_format=output_format,
    )

    assert config.output_format == output_format


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": ""}, "prompt"),
        ({"prompt": "A portrait.", "aspect_ratio": "auto"}, "aspect_ratio"),
        ({"prompt": "A portrait.", "num_images": 0}, "num_images"),
        ({"prompt": "A portrait.", "num_images": 11}, "num_images"),
        ({"prompt": "A portrait.", "output_format": "gif"}, "output_format"),
        ({"prompt": "A portrait.", "unexpected": True}, "unexpected"),
    ],
)
def test_muse_image_text_to_image_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MuseImageTextToImageConfig.model_validate({"app_id": APP_ID, **parameters})


def test_muse_image_text_to_image_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is MuseImageTextToImageConfig
    assert MuseImageTextToImageConfig.random_seed_field is None
