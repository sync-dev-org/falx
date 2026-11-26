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
    assert config.background == "auto"
    assert config.output_compression is None
    assert config.enable_safety_checker is True
    assert config.sync_mode is False


def test_gpt_image_2_config_accepts_all_fields() -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="A crisp product photo of a ceramic coffee dripper.",
        image_size="portrait_4_3",
        quality="medium",
        num_images=4,
        output_format="webp",
        background="transparent",
        output_compression=80,
        enable_safety_checker=False,
        sync_mode=True,
    )

    assert config.model_dump() == {
        "app_id": "openai/gpt-image-2",
        "prompt": "A crisp product photo of a ceramic coffee dripper.",
        "image_size": "portrait_4_3",
        "quality": "medium",
        "num_images": 4,
        "output_format": "webp",
        "background": "transparent",
        "output_compression": 80,
        "enable_safety_checker": False,
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


@pytest.mark.parametrize("num_images", [1, 10])
def test_gpt_image_2_config_accepts_num_images_boundaries(num_images: int) -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="a cat on a mat",
        num_images=num_images,
    )

    assert config.num_images == num_images


@pytest.mark.parametrize("prompt", ["a", "x" * 32_000], ids=["minimum", "maximum"])
def test_gpt_image_2_config_accepts_prompt_length_boundaries(prompt: str) -> None:
    config = GptImage2Config(app_id="openai/gpt-image-2", prompt=prompt)

    assert config.prompt == prompt


@pytest.mark.parametrize("output_compression", [None, 0, 100])
def test_gpt_image_2_config_accepts_output_compression_boundaries(
    output_compression: int | None,
) -> None:
    config = GptImage2Config(
        app_id="openai/gpt-image-2",
        prompt="a cat",
        output_format="webp",
        output_compression=output_compression,
    )

    assert config.output_compression == output_compression


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "openai/gpt-image-2"}, "prompt"),
        ({"app_id": "openai/gpt-image-2", "prompt": ""}, "prompt"),
        ({"app_id": "openai/gpt-image-2", "prompt": "x" * 32_001}, "prompt"),
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
                "num_images": 11,
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
            {"app_id": "openai/gpt-image-2", "prompt": "a cat", "background": "invalid"},
            "background",
        ),
        (
            {"app_id": "openai/gpt-image-2", "prompt": "a cat", "output_compression": -1},
            "output_compression",
        ),
        (
            {"app_id": "openai/gpt-image-2", "prompt": "a cat", "output_compression": 101},
            "output_compression",
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
