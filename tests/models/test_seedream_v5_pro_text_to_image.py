from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SeedreamV5ProImageSize, SeedreamV5ProTextToImageConfig

APP_ID = "bytedance/seedream/v5/pro/text-to-image"


def test_seedream_v5_pro_text_to_image_accepts_minimal_required_fields() -> None:
    config = SeedreamV5ProTextToImageConfig(
        app_id=APP_ID,
        prompt="A vibrant editorial portrait with dramatic studio lighting.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A vibrant editorial portrait with dramatic studio lighting.",
        "image_size": "auto_2K",
        "num_images": 1,
        "output_format": "jpeg",
        "sync_mode": False,
        "enable_safety_checker": True,
    }


def test_seedream_v5_pro_text_to_image_accepts_all_fields() -> None:
    config = SeedreamV5ProTextToImageConfig(
        app_id=APP_ID,
        prompt="A polished product photo on a mirrored pedestal.",
        image_size="auto_1K",
        num_images=6,
        output_format="png",
        sync_mode=True,
        enable_safety_checker=False,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A polished product photo on a mirrored pedestal.",
        "image_size": "auto_1K",
        "num_images": 6,
        "output_format": "png",
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
        "auto_1K",
        "auto_2K",
    ],
)
def test_seedream_v5_pro_text_to_image_accepts_image_size_presets(
    image_size: str,
) -> None:
    config = SeedreamV5ProTextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic still life.",
        image_size=image_size,
    )

    assert config.image_size == image_size


def test_seedream_v5_pro_text_to_image_accepts_custom_image_size_object() -> None:
    config = SeedreamV5ProTextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic still life.",
        image_size={"width": 1024, "height": 2048},
    )

    assert config.image_size == SeedreamV5ProImageSize(width=1024, height=2048)
    assert config.model_dump()["image_size"] == {"width": 1024, "height": 2048}


def test_seedream_v5_pro_text_to_image_schema_matches_required_and_defaults() -> None:
    schema = SeedreamV5ProTextToImageConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt"}
    assert schema["properties"]["image_size"]["default"] == "auto_2K"
    assert schema["properties"]["num_images"]["default"] == 1
    assert schema["properties"]["output_format"]["default"] == "jpeg"
    assert schema["properties"]["sync_mode"]["default"] is False
    assert schema["properties"]["enable_safety_checker"]["default"] is True

    image_size_schema = schema["$defs"]["SeedreamV5ProImageSize"]
    for dimension in ("width", "height"):
        assert image_size_schema["properties"][dimension]["default"] == 512
        assert image_size_schema["properties"][dimension]["exclusiveMinimum"] == 0
        assert image_size_schema["properties"][dimension]["maximum"] == 14142


@pytest.mark.parametrize("num_images", [1, 6])
def test_seedream_v5_pro_text_to_image_accepts_num_images_boundaries(
    num_images: int,
) -> None:
    config = SeedreamV5ProTextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic still life.",
        num_images=num_images,
    )

    assert config.num_images == num_images


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "prompt"),
        ({"app_id": APP_ID, "prompt": "A still life.", "unexpected": True}, "unexpected"),
        ({"app_id": APP_ID, "prompt": "A still life.", "image_size": "auto_3K"}, "image_size"),
        (
            {
                "app_id": APP_ID,
                "prompt": "A still life.",
                "image_size": {"width": 0, "height": 1024},
            },
            "width",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A still life.",
                "image_size": {"width": 1024, "height": 14143},
            },
            "height",
        ),
        ({"app_id": APP_ID, "prompt": "A still life.", "num_images": 0}, "num_images"),
        ({"app_id": APP_ID, "prompt": "A still life.", "num_images": 7}, "num_images"),
        ({"app_id": APP_ID, "prompt": "A still life.", "output_format": "webp"}, "output_format"),
    ],
)
def test_seedream_v5_pro_text_to_image_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SeedreamV5ProTextToImageConfig.model_validate(payload)
