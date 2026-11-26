from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SeedreamV5ProEditConfig, SeedreamV5ProImageSize

APP_ID = "bytedance/seedream/v5/pro/edit"


def test_seedream_v5_pro_edit_accepts_minimal_required_fields() -> None:
    config = SeedreamV5ProEditConfig(
        app_id=APP_ID,
        prompt="Replace the object in Figure 1 with the object in Figure 2.",
        image_urls=["https://example.com/input.png"],
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Replace the object in Figure 1 with the object in Figure 2.",
        "image_size": "auto_2K",
        "num_images": 1,
        "output_format": "jpeg",
        "watermark": False,
        "enhance_prompt_mode": "standard",
        "background": "opaque",
        "sync_mode": False,
        "enable_safety_checker": True,
        "image_urls": ["https://example.com/input.png"],
    }


def test_seedream_v5_pro_edit_accepts_all_fields() -> None:
    config = SeedreamV5ProEditConfig(
        app_id=APP_ID,
        prompt="Use the first image's subject and the second image's color palette.",
        image_size={"width": 2048, "height": 1024},
        num_images=6,
        output_format="png",
        watermark=True,
        enhance_prompt_mode="fast",
        background="transparent",
        sync_mode=True,
        enable_safety_checker=False,
        image_urls=["https://example.com/one.png", "./fixtures/two.png"],
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Use the first image's subject and the second image's color palette.",
        "image_size": {"width": 2048, "height": 1024},
        "num_images": 6,
        "output_format": "png",
        "watermark": True,
        "enhance_prompt_mode": "fast",
        "background": "transparent",
        "sync_mode": True,
        "enable_safety_checker": False,
        "image_urls": ["https://example.com/one.png", "./fixtures/two.png"],
    }
    assert config.image_size == SeedreamV5ProImageSize(width=2048, height=1024)


def test_seedream_v5_pro_edit_preserves_openapi_array_shape() -> None:
    schema = SeedreamV5ProEditConfig.model_json_schema()
    image_urls_schema = schema["properties"]["image_urls"]

    assert set(schema["required"]) == {"app_id", "prompt", "image_urls"}
    assert image_urls_schema["type"] == "array"
    assert image_urls_schema["items"] == {"type": "string"}
    assert "anyOf" not in image_urls_schema
    assert "default" not in image_urls_schema
    assert "minItems" not in image_urls_schema
    assert "maxItems" not in image_urls_schema


def test_seedream_v5_pro_edit_accepts_empty_and_more_than_ten_image_urls() -> None:
    empty = SeedreamV5ProEditConfig(
        app_id=APP_ID,
        prompt="Use automatic image selection.",
        image_urls=[],
    )
    eleven_urls = [f"https://example.com/input-{index}.png" for index in range(11)]
    over_documented_limit = SeedreamV5ProEditConfig(
        app_id=APP_ID,
        prompt="Use the endpoint's last-ten behavior.",
        image_urls=eleven_urls,
    )

    assert empty.image_urls == []
    assert over_documented_limit.image_urls == eleven_urls


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "image_urls": []}, "prompt"),
        ({"app_id": APP_ID, "prompt": "Edit the scene."}, "image_urls"),
        ({"app_id": APP_ID, "prompt": "Edit the scene.", "image_urls": None}, "image_urls"),
        (
            {
                "app_id": APP_ID,
                "prompt": "Edit the scene.",
                "image_urls": [],
                "image_size": "auto_3K",
            },
            "image_size",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Edit the scene.",
                "image_urls": [],
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_seedream_v5_pro_edit_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SeedreamV5ProEditConfig.model_validate(payload)
