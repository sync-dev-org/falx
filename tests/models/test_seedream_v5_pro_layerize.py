from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import SeedreamV5ProLayerizeConfig

APP_ID = "bytedance/seedream/v5/pro/layerize"


def test_seedream_v5_pro_layerize_accepts_minimal_required_fields() -> None:
    config = SeedreamV5ProLayerizeConfig(
        app_id=APP_ID,
        image_url="https://example.com/input.webp",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "",
        "image_url": "https://example.com/input.webp",
        "image_size": "auto",
        "sync_mode": False,
        "enable_safety_checker": True,
        "enhance_prompt_mode": "standard",
    }


def test_seedream_v5_pro_layerize_accepts_all_fields() -> None:
    config = SeedreamV5ProLayerizeConfig(
        app_id=APP_ID,
        prompt="Separate the foreground product from the background.",
        image_url="./fixtures/product.png",
        image_size="auto_1.5K",
        sync_mode=True,
        enable_safety_checker=False,
        enhance_prompt_mode="fast",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Separate the foreground product from the background.",
        "image_url": "./fixtures/product.png",
        "image_size": "auto_1.5K",
        "sync_mode": True,
        "enable_safety_checker": False,
        "enhance_prompt_mode": "fast",
    }


@pytest.mark.parametrize("image_size", ["auto", "auto_1K", "auto_1.5K", "auto_2K"])
def test_seedream_v5_pro_layerize_accepts_image_size_enum(image_size: str) -> None:
    config = SeedreamV5ProLayerizeConfig(
        app_id=APP_ID,
        image_url="https://example.com/input.webp",
        image_size=image_size,
    )

    assert config.image_size == image_size


@pytest.mark.parametrize("enhance_prompt_mode", ["standard", "fast"])
def test_seedream_v5_pro_layerize_accepts_enhance_prompt_mode_enum(
    enhance_prompt_mode: str,
) -> None:
    config = SeedreamV5ProLayerizeConfig(
        app_id=APP_ID,
        image_url="https://example.com/input.webp",
        enhance_prompt_mode=enhance_prompt_mode,
    )

    assert config.enhance_prompt_mode == enhance_prompt_mode


def test_seedream_v5_pro_layerize_schema_matches_required_and_defaults() -> None:
    schema = SeedreamV5ProLayerizeConfig.model_json_schema()

    assert schema["required"] == ["app_id", "image_url"]
    assert schema["properties"]["prompt"]["default"] == ""
    assert schema["properties"]["image_size"]["default"] == "auto"
    assert schema["properties"]["sync_mode"]["default"] is False
    assert schema["properties"]["enable_safety_checker"]["default"] is True
    assert schema["properties"]["enhance_prompt_mode"]["default"] == "standard"


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "image_url"),
        ({"app_id": APP_ID, "image_url": None}, "image_url"),
        ({"app_id": APP_ID, "image_url": "input.png", "prompt": None}, "prompt"),
        ({"app_id": APP_ID, "image_url": "input.png", "image_size": "square"}, "image_size"),
        (
            {
                "app_id": APP_ID,
                "image_url": "input.png",
                "enhance_prompt_mode": "quality",
            },
            "enhance_prompt_mode",
        ),
        ({"app_id": APP_ID, "image_url": "input.png", "unexpected": True}, "unexpected"),
    ],
)
def test_seedream_v5_pro_layerize_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SeedreamV5ProLayerizeConfig.model_validate(payload)
