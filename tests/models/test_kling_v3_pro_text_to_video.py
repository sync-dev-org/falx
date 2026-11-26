from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    KlingV3MultiPromptElement,
    KlingVideoV3ProTextToVideoConfig,
)


def test_kling_v3_pro_text_to_video_accepts_minimal_prompt_request() -> None:
    config = KlingVideoV3ProTextToVideoConfig(
        app_id="fal-ai/kling-video/v3/pro/text-to-video",
        prompt="Fireflies drift through a dark forest.",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
        "enable_safety_checker": True,
        "prompt": "Fireflies drift through a dark forest.",
        "duration": "5",
        "multi_prompt": None,
        "generate_audio": True,
        "shot_type": "customize",
        "aspect_ratio": "16:9",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
    }


def test_kling_v3_pro_text_to_video_accepts_multi_prompt_request() -> None:
    config = KlingVideoV3ProTextToVideoConfig(
        app_id="fal-ai/kling-video/v3/pro/text-to-video",
        multi_prompt=[
            KlingV3MultiPromptElement(prompt="Wide establishing shot.", duration="3"),
            KlingV3MultiPromptElement(prompt="Close-up of the subject.", duration="4"),
        ],
        duration="7",
        generate_audio=False,
        shot_type="intelligent",
        aspect_ratio="9:16",
        negative_prompt="blur",
        cfg_scale=0,
    )

    assert config.prompt is None
    assert config.duration == "7"
    assert config.aspect_ratio == "9:16"
    assert config.cfg_scale == 0


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {"app_id": "fal-ai/kling-video/v3/pro/text-to-video"},
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
                "prompt": "Wide shot.",
                "multi_prompt": [{"prompt": "Close-up."}],
            },
            "not both",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
                "prompt": "Wide shot.",
                "duration": "2",
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
                "prompt": "Wide shot.",
                "aspect_ratio": "4:3",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
                "prompt": "Wide shot.",
                "cfg_scale": -0.1,
            },
            "cfg_scale",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/text-to-video",
                "multi_prompt": [{"duration": "5"}],
            },
            "prompt",
        ),
    ],
)
def test_kling_v3_pro_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoV3ProTextToVideoConfig.model_validate(payload)
