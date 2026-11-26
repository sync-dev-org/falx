from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import KlingVideoV34kTextToVideoConfig


def test_kling_v3_4k_text_to_video_accepts_schema_defaults() -> None:
    config = KlingVideoV34kTextToVideoConfig(
        app_id="fal-ai/kling-video/v3/4k/text-to-video",
        prompt="A cinematic city street fills with morning light.",
    )

    assert config.app_id == "fal-ai/kling-video/v3/4k/text-to-video"
    assert config.duration == "5"
    assert config.generate_audio is True
    assert config.aspect_ratio == "16:9"
    assert config.shot_type == "customize"


def test_kling_v3_4k_text_to_video_accepts_4k_tier_values() -> None:
    config = KlingVideoV34kTextToVideoConfig(
        app_id="fal-ai/kling-video/v3/4k/text-to-video",
        prompt="A vertical portrait video of a dancer.",
        duration="15",
        aspect_ratio="9:16",
        cfg_scale=1,
    )

    assert config.duration == "15"
    assert config.aspect_ratio == "9:16"
    assert config.cfg_scale == 1


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {"app_id": "fal-ai/kling-video/v3/4k/text-to-video"},
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/text-to-video",
                "prompt": "Wide shot.",
                "multi_prompt": [{"prompt": "Close-up."}],
            },
            "not both",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/text-to-video",
                "prompt": "Wide shot.",
                "shot_type": "manual",
            },
            "shot_type",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/text-to-video",
                "prompt": "Wide shot.",
                "negative_prompt": "x" * 2501,
            },
            "negative_prompt",
        ),
    ],
)
def test_kling_v3_4k_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoV34kTextToVideoConfig.model_validate(payload)
