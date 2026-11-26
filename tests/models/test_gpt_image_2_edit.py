from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import GptImage2EditConfig, ImageSize


def test_gpt_image_2_edit_config_accepts_minimal_required_fields() -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=["https://example.com/input.png"],
    )

    assert config.prompt == "make the scene look like golden hour"
    assert config.image_urls == ["https://example.com/input.png"]
    assert config.image_size == "auto"
    assert config.quality == "high"
    assert config.num_images == 1
    assert config.output_format == "png"
    assert config.background == "auto"
    assert config.output_compression is None
    assert config.enable_safety_checker is True
    assert config.sync_mode is False
    assert config.mask_url is None


def test_gpt_image_2_edit_config_accepts_all_fields() -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="Replace the background with a tidy studio.",
        image_urls=["https://example.com/input.png", "./fixtures/local-input.png"],
        image_size="landscape_16_9",
        quality="low",
        num_images=4,
        output_format="jpeg",
        background="opaque",
        output_compression=75,
        enable_safety_checker=False,
        sync_mode=True,
        mask_url="https://example.com/mask.png",
    )

    assert config.model_dump() == {
        "app_id": "openai/gpt-image-2/edit",
        "prompt": "Replace the background with a tidy studio.",
        "image_size": "landscape_16_9",
        "quality": "low",
        "num_images": 4,
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
def test_gpt_image_2_edit_config_accepts_image_size_presets(image_size: str) -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=["https://example.com/input.png"],
        image_size=image_size,
    )

    assert config.image_size == image_size


def test_gpt_image_2_edit_config_accepts_image_size_object() -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=["https://example.com/input.png"],
        image_size={"width": 1280, "height": 720},
    )

    assert config.image_size == ImageSize(width=1280, height=720)
    assert config.model_dump()["image_size"] == {"width": 1280, "height": 720}


@pytest.mark.parametrize("quality", ["auto", "low", "medium", "high"])
def test_gpt_image_2_edit_config_accepts_quality_enum(quality: str) -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=["https://example.com/input.png"],
        quality=quality,
    )

    assert config.quality == quality


@pytest.mark.parametrize("num_images", [1, 10])
def test_gpt_image_2_edit_config_accepts_num_images_boundaries(num_images: int) -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="make the scene look like golden hour",
        image_urls=["https://example.com/input.png"],
        num_images=num_images,
    )

    assert config.num_images == num_images


@pytest.mark.parametrize("image_count", [0, 16])
def test_gpt_image_2_edit_config_accepts_image_urls_boundaries(image_count: int) -> None:
    image_urls = [f"https://example.com/input-{index}.png" for index in range(image_count)]

    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit", prompt="make it warm", image_urls=image_urls
    )

    assert config.image_urls == image_urls


@pytest.mark.parametrize("prompt", ["a", "x" * 32_000], ids=["minimum", "maximum"])
def test_gpt_image_2_edit_config_accepts_prompt_length_boundaries(prompt: str) -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt=prompt,
        image_urls=["https://example.com/input.png"],
    )

    assert config.prompt == prompt


@pytest.mark.parametrize("output_compression", [None, 0, 100])
def test_gpt_image_2_edit_config_accepts_output_compression_boundaries(
    output_compression: int | None,
) -> None:
    config = GptImage2EditConfig(
        app_id="openai/gpt-image-2/edit",
        prompt="make it warm",
        image_urls=["https://example.com/input.png"],
        output_format="jpeg",
        output_compression=output_compression,
    )

    assert config.output_compression == output_compression


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "openai/gpt-image-2/edit"}, "prompt"),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
            },
            "image_urls",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": [f"https://example.com/input-{index}.png" for index in range(17)],
            },
            "image_urls",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "",
                "image_urls": ["https://example.com/input.png"],
            },
            "prompt",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "quality": "ultra",
            },
            "quality",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "num_images": 0,
            },
            "num_images",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "num_images": 11,
            },
            "num_images",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "output_format": "gif",
            },
            "output_format",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": [],
                "background": "invalid",
            },
            "background",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": [],
                "output_compression": -1,
            },
            "output_compression",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": [],
                "output_compression": 101,
            },
            "output_compression",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "image_size": "cinemascope",
            },
            "image_size",
        ),
        (
            {
                "app_id": "openai/gpt-image-2/edit",
                "prompt": "make it warm",
                "image_urls": ["https://example.com/input.png"],
                "image_size": {"width": 1280, "height": 720, "unit": "px"},
            },
            "unit",
        ),
    ],
)
def test_gpt_image_2_edit_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GptImage2EditConfig(**payload)
