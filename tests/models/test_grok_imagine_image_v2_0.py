from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    GrokImagineImageV20TextToImageConfig,
    config_class_for_app_id,
)

APP_ID = "xai/grok-imagine-image/v2.0/text-to-image"
ASPECT_RATIOS = [
    "2:1",
    "20:9",
    "19.5:9",
    "16:9",
    "4:3",
    "3:2",
    "1:1",
    "2:3",
    "3:4",
    "9:16",
    "9:19.5",
    "9:20",
    "1:2",
    "auto",
    "21:9",
    "5:2",
]


def test_grok_imagine_image_v2_0_text_to_image_accepts_schema_defaults() -> None:
    config = GrokImagineImageV20TextToImageConfig(
        app_id=APP_ID,
        prompt="An abstract human silhouette made of golden particles.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "An abstract human silhouette made of golden particles.",
        "aspect_ratio": "1:1",
        "resolution": "1k",
        "quality": "medium",
        "num_images": 1,
        "output_format": "jpeg",
        "sync_mode": False,
        "enable_safety_checker": True,
    }


def test_grok_imagine_image_v2_0_text_to_image_accepts_all_fields() -> None:
    config = GrokImagineImageV20TextToImageConfig(
        app_id=APP_ID,
        prompt="An abstract human silhouette made of golden particles.",
        aspect_ratio="20:9",
        resolution="2k",
        quality="low",
        num_images=4,
        output_format="webp",
        sync_mode=True,
        enable_safety_checker=False,
    )

    assert config.aspect_ratio == "20:9"
    assert config.resolution == "2k"
    assert config.quality == "low"
    assert config.num_images == 4
    assert config.output_format == "webp"
    assert config.sync_mode is True
    assert config.enable_safety_checker is False


@pytest.mark.parametrize("aspect_ratio", ASPECT_RATIOS)
def test_grok_imagine_image_v2_0_text_to_image_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = GrokImagineImageV20TextToImageConfig(
        app_id=APP_ID,
        prompt="An abstract portrait.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("resolution", ["1k", "1.5k", "2k"])
@pytest.mark.parametrize("quality", ["low", "medium", "auto"])
@pytest.mark.parametrize("num_images", [1, 10])
def test_grok_imagine_image_v2_0_text_to_image_accepts_common_enums_and_boundaries(
    resolution: str,
    quality: str,
    num_images: int,
) -> None:
    config = GrokImagineImageV20TextToImageConfig(
        app_id=APP_ID,
        prompt="An abstract portrait.",
        resolution=resolution,
        quality=quality,
        num_images=num_images,
    )

    assert config.resolution == resolution
    assert config.quality == quality
    assert config.num_images == num_images


@pytest.mark.parametrize("output_format", ["jpeg", "png", "webp"])
def test_grok_imagine_image_v2_0_text_to_image_accepts_output_format_enum(
    output_format: str,
) -> None:
    config = GrokImagineImageV20TextToImageConfig(
        app_id=APP_ID,
        prompt="An abstract portrait.",
        output_format=output_format,
    )

    assert config.output_format == output_format


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": "x" * 8001}, "prompt"),
        ({"prompt": "An abstract portrait.", "aspect_ratio": "3:1"}, "aspect_ratio"),
        ({"prompt": "An abstract portrait.", "resolution": "4k"}, "resolution"),
        ({"prompt": "An abstract portrait.", "quality": "high"}, "quality"),
        ({"prompt": "An abstract portrait.", "num_images": 0}, "num_images"),
        ({"prompt": "An abstract portrait.", "num_images": 11}, "num_images"),
        (
            {"prompt": "An abstract portrait.", "enable_safety_checker": None},
            "enable_safety_checker",
        ),
        ({"prompt": "An abstract portrait.", "output_format": "gif"}, "output_format"),
        ({"prompt": "An abstract portrait.", "unexpected": True}, "unexpected"),
    ],
)
def test_grok_imagine_image_v2_0_text_to_image_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineImageV20TextToImageConfig.model_validate({"app_id": APP_ID, **parameters})


def test_grok_imagine_image_v2_0_text_to_image_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is GrokImagineImageV20TextToImageConfig
    assert GrokImagineImageV20TextToImageConfig.random_seed_field is None
