from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    GptImage25FlareTextToImageConfig,
    GptImage25SunburstTextToImageConfig,
    ImageSize,
)

TEXT_TO_IMAGE_CONFIGS = [
    (
        GptImage25FlareTextToImageConfig,
        "openai/gpt-image-2.5/flare/text-to-image",
    ),
    (
        GptImage25SunburstTextToImageConfig,
        "openai/gpt-image-2.5/sunburst/text-to-image",
    ),
]


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
def test_gpt_image_2_5_text_to_image_accepts_schema_defaults(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
) -> None:
    config = config_class(app_id=app_id, prompt="a cat on a mat")

    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "a cat on a mat",
        "image_size": "landscape_4_3",
        "quality": "high",
        "num_images": 1,
        "output_format": "png",
        "background": "auto",
        "output_compression": None,
        "sync_mode": False,
    }


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
def test_gpt_image_2_5_text_to_image_accepts_all_fields(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="A crisp product photo of a ceramic coffee dripper.",
        image_size="portrait_4_3",
        quality="max",
        num_images=10,
        output_format="webp",
        background="transparent",
        output_compression=80,
        sync_mode=True,
    )

    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "A crisp product photo of a ceramic coffee dripper.",
        "image_size": "portrait_4_3",
        "quality": "max",
        "num_images": 10,
        "output_format": "webp",
        "background": "transparent",
        "output_compression": 80,
        "sync_mode": True,
    }


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
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
def test_gpt_image_2_5_text_to_image_accepts_image_size_presets(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
    image_size: str,
) -> None:
    config = config_class(app_id=app_id, prompt="a cat", image_size=image_size)

    assert config.image_size == image_size


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
def test_gpt_image_2_5_text_to_image_reuses_image_size_object(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="a cat",
        image_size={"width": 1280, "height": 720},
    )

    assert config.image_size == ImageSize(width=1280, height=720)
    assert config.model_dump()["image_size"] == {"width": 1280, "height": 720}


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
@pytest.mark.parametrize("quality", ["auto", "low", "medium", "high", "xhigh", "max"])
def test_gpt_image_2_5_text_to_image_accepts_quality_enum(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
    quality: str,
) -> None:
    config = config_class(app_id=app_id, prompt="a cat", quality=quality)

    assert config.quality == quality


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
@pytest.mark.parametrize("num_images", [1, 10])
def test_gpt_image_2_5_text_to_image_accepts_num_images_boundaries(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
    num_images: int,
) -> None:
    config = config_class(app_id=app_id, prompt="a cat", num_images=num_images)

    assert config.num_images == num_images


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
@pytest.mark.parametrize("output_compression", [None, 0, 100])
def test_gpt_image_2_5_text_to_image_accepts_output_compression_boundaries(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
    output_compression: int | None,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="a cat",
        output_format="png",
        output_compression=output_compression,
    )

    assert config.output_compression == output_compression


@pytest.mark.parametrize(("config_class", "app_id"), TEXT_TO_IMAGE_CONFIGS)
@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": ""}, "prompt"),
        ({"prompt": "x" * 32_001}, "prompt"),
        ({"prompt": "a cat", "unexpected": True}, "unexpected"),
        ({"prompt": "a cat", "quality": "ultra"}, "quality"),
        ({"prompt": "a cat", "num_images": 0}, "num_images"),
        ({"prompt": "a cat", "num_images": 11}, "num_images"),
        ({"prompt": "a cat", "output_format": "gif"}, "output_format"),
        ({"prompt": "a cat", "background": "checkerboard"}, "background"),
        ({"prompt": "a cat", "output_compression": -1}, "output_compression"),
        ({"prompt": "a cat", "output_compression": 101}, "output_compression"),
        ({"prompt": "a cat", "image_size": "cinemascope"}, "image_size"),
    ],
)
def test_gpt_image_2_5_text_to_image_rejects_invalid_payloads(
    config_class: type[GptImage25FlareTextToImageConfig],
    app_id: str,
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        config_class(app_id=app_id, **parameters)
