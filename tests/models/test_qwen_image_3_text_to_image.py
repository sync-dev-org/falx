from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import QwenImage3ImageSize, QwenImage3TextToImageConfig

APP_ID = "alibaba/qwen-image-3/text-to-image"


def test_qwen_image_3_text_to_image_accepts_schema_defaults() -> None:
    config = QwenImage3TextToImageConfig(
        app_id=APP_ID,
        prompt="A product photo of a ceramic tea set.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A product photo of a ceramic tea set.",
        "negative_prompt": "",
        "image_size": "square_hd",
        "enable_prompt_expansion": True,
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "num_images": 1,
        "output_format": "png",
    }


def test_qwen_image_3_text_to_image_accepts_all_fields() -> None:
    config = QwenImage3TextToImageConfig(
        app_id=APP_ID,
        prompt="A bright editorial photograph.",
        negative_prompt=None,
        image_size={"width": 14142, "height": 1},
        enable_prompt_expansion=False,
        seed=2_147_483_647,
        enable_safety_checker=False,
        sync_mode=True,
        num_images=6,
        output_format="webp",
    )

    assert config.image_size == QwenImage3ImageSize(width=14142, height=1)
    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A bright editorial photograph.",
        "negative_prompt": None,
        "image_size": {"width": 14142, "height": 1},
        "enable_prompt_expansion": False,
        "seed": 2_147_483_647,
        "enable_safety_checker": False,
        "sync_mode": True,
        "num_images": 6,
        "output_format": "webp",
    }


def test_qwen_image_3_text_to_image_schema_preserves_required_fields_and_defaults() -> None:
    schema = QwenImage3TextToImageConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt"}
    properties = schema["properties"]
    assert properties["negative_prompt"]["default"] == ""
    assert properties["image_size"]["default"] == "square_hd"
    assert properties["enable_prompt_expansion"]["default"] is True
    assert properties["seed"]["default"] is None
    assert properties["enable_safety_checker"]["default"] is True
    assert properties["sync_mode"]["default"] is False
    assert properties["num_images"]["default"] == 1
    assert properties["output_format"]["default"] == "png"


@pytest.mark.parametrize(
    "image_size",
    [
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
    ],
)
def test_qwen_image_3_text_to_image_accepts_image_size_presets(
    image_size: str,
) -> None:
    config = QwenImage3TextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic still life.",
        image_size=image_size,
    )

    assert config.image_size == image_size


@pytest.mark.parametrize("output_format", ["jpeg", "png", "webp"])
def test_qwen_image_3_text_to_image_accepts_output_formats(
    output_format: str,
) -> None:
    config = QwenImage3TextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic still life.",
        output_format=output_format,
    )

    assert config.output_format == output_format


@pytest.mark.parametrize("seed", [None, 0, 2_147_483_647])
def test_qwen_image_3_text_to_image_accepts_seed_boundaries(
    seed: int | None,
) -> None:
    config = QwenImage3TextToImageConfig(
        app_id=APP_ID,
        prompt="A cinematic still life.",
        seed=seed,
    )

    assert config.seed == seed


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "prompt"),
        ({"app_id": APP_ID, "prompt": ""}, "prompt"),
        ({"app_id": APP_ID, "prompt": "x" * 5001}, "prompt"),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "negative_prompt": "x" * 501,
            },
            "negative_prompt",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "image_size": None,
            },
            "image_size",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "image_size": "auto",
            },
            "image_size",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "image_size": {"width": 0, "height": 512},
            },
            "width",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "image_size": {"width": 512, "height": 14143},
            },
            "height",
        ),
        ({"app_id": APP_ID, "prompt": "A cinematic still life.", "seed": -1}, "seed"),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "seed": 2_147_483_648,
            },
            "seed",
        ),
        (
            {"app_id": APP_ID, "prompt": "A cinematic still life.", "num_images": 0},
            "num_images",
        ),
        (
            {"app_id": APP_ID, "prompt": "A cinematic still life.", "num_images": 7},
            "num_images",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "A cinematic still life.",
                "output_format": "gif",
            },
            "output_format",
        ),
        (
            {"app_id": APP_ID, "prompt": "A cinematic still life.", "unexpected": True},
            "unexpected",
        ),
    ],
)
def test_qwen_image_3_text_to_image_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        QwenImage3TextToImageConfig.model_validate(payload)
