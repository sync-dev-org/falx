from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    GptImage25FlareEditConfig,
    GptImage25SunburstEditConfig,
    ImageSize,
)

EDIT_CONFIGS = [
    (GptImage25FlareEditConfig, "openai/gpt-image-2.5/flare/edit"),
    (GptImage25SunburstEditConfig, "openai/gpt-image-2.5/sunburst/edit"),
]


@pytest.mark.parametrize(("config_class", "app_id"), EDIT_CONFIGS)
def test_gpt_image_2_5_edit_accepts_schema_defaults(
    config_class: type[GptImage25FlareEditConfig],
    app_id: str,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="make the scene look like golden hour",
        image_urls=["https://example.com/input.png"],
    )

    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "make the scene look like golden hour",
        "image_size": "auto",
        "quality": "high",
        "num_images": 1,
        "output_format": "png",
        "background": "auto",
        "output_compression": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "image_urls": ["https://example.com/input.png"],
        "mask_url": None,
    }


@pytest.mark.parametrize(("config_class", "app_id"), EDIT_CONFIGS)
def test_gpt_image_2_5_edit_accepts_all_fields(
    config_class: type[GptImage25FlareEditConfig],
    app_id: str,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="Replace the background with a tidy studio.",
        image_urls=["https://example.com/input.png", "./fixtures/local-input.png"],
        image_size="landscape_16_9",
        quality="xhigh",
        num_images=10,
        output_format="jpeg",
        background="opaque",
        output_compression=75,
        enable_safety_checker=False,
        sync_mode=True,
        mask_url="https://example.com/mask.png",
    )

    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "Replace the background with a tidy studio.",
        "image_size": "landscape_16_9",
        "quality": "xhigh",
        "num_images": 10,
        "output_format": "jpeg",
        "background": "opaque",
        "output_compression": 75,
        "enable_safety_checker": False,
        "sync_mode": True,
        "image_urls": [
            "https://example.com/input.png",
            "./fixtures/local-input.png",
        ],
        "mask_url": "https://example.com/mask.png",
    }


@pytest.mark.parametrize(("config_class", "app_id"), EDIT_CONFIGS)
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
def test_gpt_image_2_5_edit_accepts_image_size_presets(
    config_class: type[GptImage25FlareEditConfig],
    app_id: str,
    image_size: str,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="make it warm",
        image_urls=[],
        image_size=image_size,
    )

    assert config.image_size == image_size


@pytest.mark.parametrize(("config_class", "app_id"), EDIT_CONFIGS)
def test_gpt_image_2_5_edit_reuses_image_size_object(
    config_class: type[GptImage25FlareEditConfig],
    app_id: str,
) -> None:
    config = config_class(
        app_id=app_id,
        prompt="make it warm",
        image_urls=[],
        image_size={"width": 1280, "height": 720},
    )

    assert config.image_size == ImageSize(width=1280, height=720)


@pytest.mark.parametrize(("config_class", "app_id"), EDIT_CONFIGS)
@pytest.mark.parametrize("image_count", [0, 16])
def test_gpt_image_2_5_edit_accepts_image_urls_boundaries(
    config_class: type[GptImage25FlareEditConfig],
    app_id: str,
    image_count: int,
) -> None:
    image_urls = [f"https://example.com/input-{index}.png" for index in range(image_count)]

    config = config_class(app_id=app_id, prompt="make it warm", image_urls=image_urls)

    assert config.image_urls == image_urls


@pytest.mark.parametrize(("config_class", "app_id"), EDIT_CONFIGS)
@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"image_urls": []}, "prompt"),
        ({"prompt": "make it warm"}, "image_urls"),
        (
            {
                "prompt": "make it warm",
                "image_urls": [f"https://example.com/input-{index}.png" for index in range(17)],
            },
            "image_urls",
        ),
        ({"prompt": "make it warm", "image_urls": [], "quality": "ultra"}, "quality"),
        (
            {"prompt": "make it warm", "image_urls": [], "output_compression": -1},
            "output_compression",
        ),
        (
            {"prompt": "make it warm", "image_urls": [], "output_compression": 101},
            "output_compression",
        ),
        ({"prompt": "make it warm", "image_urls": [], "unexpected": True}, "unexpected"),
    ],
)
def test_gpt_image_2_5_edit_rejects_invalid_payloads(
    config_class: type[GptImage25FlareEditConfig],
    app_id: str,
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        config_class(app_id=app_id, **parameters)
