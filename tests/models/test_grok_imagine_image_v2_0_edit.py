from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    GrokImagineImageV20EditConfig,
    config_class_for_app_id,
)

APP_ID = "xai/grok-imagine-image/v2.0/edit"
ASPECT_RATIOS = [
    "auto",
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
    "21:9",
    "5:2",
]


def test_grok_imagine_image_v2_0_edit_accepts_schema_defaults() -> None:
    config = GrokImagineImageV20EditConfig(
        app_id=APP_ID,
        prompt="Make the scene more realistic.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Make the scene more realistic.",
        "aspect_ratio": "auto",
        "resolution": "1k",
        "quality": "medium",
        "num_images": 1,
        "output_format": "jpeg",
        "sync_mode": False,
        "enable_safety_checker": True,
        "image_urls": None,
    }


def test_grok_imagine_image_v2_0_edit_accepts_all_fields() -> None:
    config = GrokImagineImageV20EditConfig(
        app_id=APP_ID,
        prompt="Make the scene more realistic.",
        aspect_ratio="16:9",
        resolution="2k",
        quality="low",
        num_images=4,
        output_format="png",
        sync_mode=True,
        enable_safety_checker=False,
        image_urls=[f"https://example.com/source-{index}.png" for index in range(5)],
    )

    assert config.aspect_ratio == "16:9"
    assert config.resolution == "2k"
    assert config.quality == "low"
    assert config.num_images == 4
    assert config.output_format == "png"
    assert config.sync_mode is True
    assert config.enable_safety_checker is False
    assert len(config.image_urls or []) == 5


@pytest.mark.parametrize("aspect_ratio", ASPECT_RATIOS)
def test_grok_imagine_image_v2_0_edit_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = GrokImagineImageV20EditConfig(
        app_id=APP_ID,
        prompt="Edit the image.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("image_urls", [None, [], ["1"], ["1", "2", "3", "4", "5"]])
def test_grok_imagine_image_v2_0_edit_accepts_optional_image_urls_up_to_five(
    image_urls: list[str] | None,
) -> None:
    config = GrokImagineImageV20EditConfig(
        app_id=APP_ID,
        prompt="Edit the image.",
        image_urls=image_urls,
    )

    assert config.image_urls == image_urls


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": "x" * 8001}, "prompt"),
        ({"prompt": "Edit the image.", "aspect_ratio": "3:1"}, "aspect_ratio"),
        (
            {"prompt": "Edit the image.", "image_urls": ["1", "2", "3", "4", "5", "6"]},
            "image_urls",
        ),
        ({"prompt": "Edit the image.", "num_images": 0}, "num_images"),
        ({"prompt": "Edit the image.", "num_images": 11}, "num_images"),
        ({"prompt": "Edit the image.", "quality": "high"}, "quality"),
        ({"prompt": "Edit the image.", "resolution": "4k"}, "resolution"),
        (
            {"prompt": "Edit the image.", "enable_safety_checker": None},
            "enable_safety_checker",
        ),
        ({"prompt": "Edit the image.", "unexpected": True}, "unexpected"),
    ],
)
def test_grok_imagine_image_v2_0_edit_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineImageV20EditConfig.model_validate({"app_id": APP_ID, **parameters})


def test_grok_imagine_image_v2_0_edit_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is GrokImagineImageV20EditConfig
    assert GrokImagineImageV20EditConfig.random_seed_field is None


def test_grok_imagine_image_v2_0_edit_schema_describes_edited_image_quality() -> None:
    schema = GrokImagineImageV20EditConfig.model_json_schema()
    quality = schema["properties"]["quality"]

    assert "Quality level of the edited image." in quality["description"]
    assert "`auto`" in quality["description"]
    assert quality["default"] == "medium"
    assert quality["enum"] == ["low", "medium", "auto"]


@pytest.mark.parametrize(
    ("field", "value"),
    [("resolution", "1.5k"), ("quality", "auto"), ("num_images", 10)],
)
def test_grok_imagine_image_v2_0_edit_accepts_current_image_options(
    field: str,
    value: str | int,
) -> None:
    config = GrokImagineImageV20EditConfig.model_validate(
        {"app_id": APP_ID, "prompt": "Edit the image.", field: value}
    )

    assert config.model_dump(exclude={"app_id"})[field] == value
