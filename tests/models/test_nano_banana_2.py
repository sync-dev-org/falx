from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import NanoBanana2Config


def test_nano_banana_2_config_accepts_minimal_required_fields() -> None:
    config = NanoBanana2Config(app_id="fal-ai/nano-banana-2", prompt="a cat on a mat")

    assert config.prompt == "a cat on a mat"
    assert config.num_images == 1
    assert config.limit_generations is True
    assert config.sync_mode is False
    assert config.resolution == "1K"
    assert config.aspect_ratio == "auto"
    assert config.output_format == "png"
    assert config.thinking_level is None
    assert config.safety_tolerance == "4"
    assert config.enable_web_search is False
    assert config.system_prompt == ""
    assert config.seed is None


def test_nano_banana_2_config_accepts_all_fields() -> None:
    config = NanoBanana2Config(
        app_id="fal-ai/nano-banana-2",
        prompt="An action shot of a black lab swimming in an inground suburban pool.",
        num_images=4,
        limit_generations=False,
        sync_mode=True,
        resolution="4K",
        aspect_ratio="16:9",
        output_format="jpeg",
        thinking_level="high",
        safety_tolerance="6",
        enable_web_search=True,
        system_prompt="Use a polished editorial illustration style.",
        seed=42,
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/nano-banana-2",
        "prompt": "An action shot of a black lab swimming in an inground suburban pool.",
        "num_images": 4,
        "limit_generations": False,
        "sync_mode": True,
        "resolution": "4K",
        "aspect_ratio": "16:9",
        "output_format": "jpeg",
        "thinking_level": "high",
        "safety_tolerance": "6",
        "enable_web_search": True,
        "system_prompt": "Use a polished editorial illustration style.",
        "seed": 42,
        "history": [],
        "context": [],
        "return_history": False,
        "include_thoughts": None,
        "temperature": None,
        "top_p": None,
        "max_output_tokens": None,
        "enable_image_search": False,
    }


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {"app_id": "fal-ai/nano-banana-2", "prompt": "a cat", "unexpected": True},
            "unexpected",
        ),
        (
            {"app_id": "fal-ai/nano-banana-2", "prompt": "a cat", "resolution": "8K"},
            "resolution",
        ),
        (
            {"app_id": "fal-ai/nano-banana-2", "prompt": "a cat", "num_images": "abc"},
            "num_images",
        ),
        (
            {"app_id": "fal-ai/nano-banana-2"},
            "prompt",
        ),
        (
            {"app_id": "fal-ai/nano-banana-2", "prompt": "a cat", "num_images": 5},
            "num_images",
        ),
        (
            {"app_id": "fal-ai/nano-banana-2", "prompt": "no"},
            "prompt",
        ),
    ],
)
def test_nano_banana_2_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        NanoBanana2Config(**payload)
