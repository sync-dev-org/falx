from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import GptImage2Config, ImageSize


def test_gpt_image_2_config_accepts_minimal_required_fields() -> None:
    config = GptImage2Config(app_id="openai/gpt-image-2", prompt="a cat on a mat")

    assert config.prompt == "a cat on a mat"
    assert config.image_size == "landscape_4_3"
    assert config.quality == "high"
    assert config.num_images == 1
    assert config.output_format == "png"
    assert config.sync_mode is False


def test_gpt_image_2_config_accepts_all_fields() -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="A crisp product photo of a ceramic coffee dripper.",
        image_size="portrait_4_3",
        quality="medium",
        num_images=4,
        output_format="webp",
        sync_mode=True,
    )

    assert config.model_dump() == {
        "app_id": "openai/gpt-image-2",
        "prompt": "A crisp product photo of a ceramic coffee dripper.",
        "image_size": "portrait_4_3",
        "quality": "medium",
        "num_images": 4,
        "output_format": "webp",
        "sync_mode": True,
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
        "auto",
    ],
)
def test_gpt_image_2_config_accepts_image_size_presets(image_size: str) -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="a cat on a mat",
        image_size=image_size,
    )

    assert config.image_size == image_size


def test_gpt_image_2_config_accepts_image_size_object() -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="a cat on a mat",
        image_size={"width": 1280, "height": 720},
    )

    assert config.image_size == ImageSize(width=1280, height=720)
    assert config.model_dump()["image_size"] == {"width": 1280, "height": 720}


@pytest.mark.parametrize("quality", ["auto", "low", "medium", "high"])
def test_gpt_image_2_config_accepts_quality_enum(quality: str) -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="a cat on a mat",
        quality=quality,
    )

    assert config.quality == quality


@pytest.mark.parametrize("num_images", [1, 4])
def test_gpt_image_2_config_accepts_num_images_boundaries(num_images: int) -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="a cat on a mat",
        num_images=num_images,
    )

    assert config.num_images == num_images


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "openai/gpt-image-2"}, "prompt"),
        ({"app_id": "openai/gpt-image-2", "prompt": "a"}, "prompt"),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "quality": "ultra",
            },
            "quality",
        ),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "num_images": 0,
            },
            "num_images",
        ),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "num_images": 5,
            },
            "num_images",
        ),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "output_format": "gif",
            },
            "output_format",
        ),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "image_size": "cinemascope",
            },
            "image_size",
        ),
        (
            {
                "app_id": "openai/gpt-image-2",
                "prompt": "a cat",
                "image_size": {"width": 1280, "height": 720, "unit": "px"},
            },
            "unit",
        ),
    ],
)
def test_gpt_image_2_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GptImage2Config(**payload)
