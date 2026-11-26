from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import QwenImage3EditConfig, QwenImage3ImageSize

APP_ID = "alibaba/qwen-image-3/edit"


def test_qwen_image_3_edit_accepts_schema_defaults() -> None:
    config = QwenImage3EditConfig(
        app_id=APP_ID,
        prompt="Replace the background with a mountain landscape.",
        image_urls=["https://example.com/input.png"],
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Replace the background with a mountain landscape.",
        "negative_prompt": "",
        "image_size": None,
        "enable_prompt_expansion": True,
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "num_images": 1,
        "output_format": "png",
        "image_urls": ["https://example.com/input.png"],
    }


def test_qwen_image_3_edit_accepts_all_fields() -> None:
    config = QwenImage3EditConfig(
        app_id=APP_ID,
        prompt="Make the scene look like golden hour.",
        negative_prompt=None,
        image_size={"width": 2048, "height": 1024},
        enable_prompt_expansion=False,
        seed=0,
        enable_safety_checker=False,
        sync_mode=True,
        num_images=6,
        output_format="jpeg",
        image_urls=[
            "https://example.com/source.png",
            "./fixtures/reference.png",
        ],
    )

    assert config.image_size == QwenImage3ImageSize(width=2048, height=1024)
    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Make the scene look like golden hour.",
        "negative_prompt": None,
        "image_size": {"width": 2048, "height": 1024},
        "enable_prompt_expansion": False,
        "seed": 0,
        "enable_safety_checker": False,
        "sync_mode": True,
        "num_images": 6,
        "output_format": "jpeg",
        "image_urls": [
            "https://example.com/source.png",
            "./fixtures/reference.png",
        ],
    }


def test_qwen_image_3_edit_schema_preserves_required_array_contract() -> None:
    schema = QwenImage3EditConfig.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt", "image_urls"}
    image_urls_schema = schema["properties"]["image_urls"]
    assert image_urls_schema["type"] == "array"
    assert "anyOf" not in image_urls_schema
    assert "default" not in image_urls_schema
    assert "minItems" not in image_urls_schema
    assert "maxItems" not in image_urls_schema


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "image_urls": ["https://example.com/input.png"]}, "prompt"),
        ({"app_id": APP_ID, "prompt": "Make the scene warmer."}, "image_urls"),
        (
            {"app_id": APP_ID, "prompt": "Make the scene warmer.", "image_urls": None},
            "image_urls",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Make the scene warmer.",
                "image_urls": "https://example.com/input.png",
            },
            "image_urls",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Make the scene warmer.",
                "image_urls": ["https://example.com/input.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_qwen_image_3_edit_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        QwenImage3EditConfig.model_validate(payload)
