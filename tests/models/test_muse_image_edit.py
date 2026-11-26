from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    MuseImageEditConfig,
    config_class_for_app_id,
)

APP_ID = "meta/muse-image/edit"


@pytest.mark.parametrize("aspect_ratio", ["5:4", "1920:1200", "1:16", "16:1"])
def test_muse_image_edit_accepts_custom_aspect_ratios(aspect_ratio: str) -> None:
    config = MuseImageEditConfig(
        app_id=APP_ID,
        prompt="Edit the image.",
        image_urls=["https://example.com/source.png"],
        aspect_ratio=aspect_ratio,
    )

    assert config.model_dump(exclude={"app_id"})["aspect_ratio"] == aspect_ratio


@pytest.mark.parametrize("aspect_ratio", ["0:1", "100000:100000", "1:17", "17:1"])
def test_muse_image_edit_rejects_invalid_custom_aspect_ratios(aspect_ratio: str) -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        MuseImageEditConfig(
            app_id=APP_ID,
            prompt="Edit the image.",
            image_urls=["https://example.com/source.png"],
            aspect_ratio=aspect_ratio,
        )


def test_muse_image_edit_accepts_schema_defaults() -> None:
    config = MuseImageEditConfig(
        app_id=APP_ID,
        prompt="Turn the scene into a watercolor.",
        image_urls=["https://example.com/source.png"],
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Turn the scene into a watercolor.",
        "aspect_ratio": None,
        "num_images": 1,
        "output_format": "webp",
        "sync_mode": False,
        "image_urls": ["https://example.com/source.png"],
    }


def test_muse_image_edit_accepts_all_fields() -> None:
    config = MuseImageEditConfig(
        app_id=APP_ID,
        prompt="Turn the scene into a watercolor.",
        image_urls=[f"https://example.com/source-{index}.png" for index in range(10)],
        aspect_ratio="16:9",
        num_images=10,
        output_format="jpeg",
        sync_mode=True,
    )

    assert len(config.image_urls) == 10
    assert config.aspect_ratio == "16:9"
    assert config.num_images == 10
    assert config.output_format == "jpeg"
    assert config.sync_mode is True


@pytest.mark.parametrize("image_count", [1, 10])
def test_muse_image_edit_accepts_image_url_boundaries(image_count: int) -> None:
    config = MuseImageEditConfig(
        app_id=APP_ID,
        prompt="Edit the image.",
        image_urls=[f"https://example.com/source-{index}.png" for index in range(image_count)],
    )

    assert len(config.image_urls) == image_count


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"image_urls": ["https://example.com/source.png"]}, "prompt"),
        ({"prompt": "Edit the image."}, "image_urls"),
        ({"prompt": "Edit the image.", "image_urls": []}, "image_urls"),
        (
            {
                "prompt": "Edit the image.",
                "image_urls": [f"https://example.com/{index}.png" for index in range(11)],
            },
            "image_urls",
        ),
        (
            {
                "prompt": "Edit the image.",
                "image_urls": ["https://example.com/source.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_muse_image_edit_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MuseImageEditConfig.model_validate({"app_id": APP_ID, **parameters})


def test_muse_image_edit_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is MuseImageEditConfig
    assert MuseImageEditConfig.random_seed_field is None


def test_muse_image_edit_schema_describes_edited_images() -> None:
    schema = MuseImageEditConfig.model_json_schema()
    num_images = schema["properties"]["num_images"]

    assert num_images["description"] == "The number of edited images to generate."
    assert num_images["default"] == 1
    assert num_images["minimum"] == 1
    assert num_images["maximum"] == 10
