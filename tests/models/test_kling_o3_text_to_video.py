from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    KlingO3MultiPromptElement,
    KlingVideoO3ProTextToVideoConfig,
    KlingVideoO34kTextToVideoConfig,
)


def test_kling_o3_pro_text_to_video_accepts_schema_defaults() -> None:
    config = KlingVideoO3ProTextToVideoConfig(
        app_id="fal-ai/kling-video/o3/pro/text-to-video",
        prompt='A mecha lands on the ground and says "I am here".',
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
        "prompt": 'A mecha lands on the ground and says "I am here".',
        "aspect_ratio": "16:9",
        "shot_type": "customize",
        "duration": "5",
        "generate_audio": False,
        "multi_prompt": None,
    }


def test_kling_o3_4k_text_to_video_accepts_multi_prompt() -> None:
    config = KlingVideoO34kTextToVideoConfig(
        app_id="fal-ai/kling-video/o3/4k/text-to-video",
        multi_prompt=[
            KlingO3MultiPromptElement(prompt="Wide establishing shot.", duration="4"),
            KlingO3MultiPromptElement(prompt="Close-up of the pilot.", duration="6"),
        ],
        aspect_ratio="9:16",
        shot_type="intelligent",
        duration="10",
        generate_audio=True,
    )

    assert config.prompt is None
    assert config.app_id == "fal-ai/kling-video/o3/4k/text-to-video"
    assert config.aspect_ratio == "9:16"
    assert config.shot_type == "intelligent"
    assert config.duration == "10"
    assert config.generate_audio is True


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {"app_id": "fal-ai/kling-video/o3/pro/text-to-video"},
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
                "prompt": "Wide shot.",
                "multi_prompt": [{"prompt": "Close-up."}],
            },
            "not both",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
                "prompt": "x" * 2501,
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
                "prompt": "Wide shot.",
                "duration": "2",
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
                "prompt": "Wide shot.",
                "aspect_ratio": "4:3",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/text-to-video",
                "multi_prompt": [{"duration": "5"}],
            },
            "prompt",
        ),
    ],
)
def test_kling_o3_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoO3ProTextToVideoConfig.model_validate(payload)
