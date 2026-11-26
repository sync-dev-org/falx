from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    KlingO3MultiPromptElement,
    KlingVideoO3ProImageToVideoConfig,
    KlingVideoO34kImageToVideoConfig,
)


def test_kling_o3_pro_image_to_video_accepts_schema_defaults() -> None:
    config = KlingVideoO3ProImageToVideoConfig(
        app_id="fal-ai/kling-video/o3/pro/image-to-video",
        prompt="The character walks forward slowly.",
        image_url="https://example.com/start.png",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
        "enable_safety_checker": True,
        "prompt": "The character walks forward slowly.",
        "image_url": "https://example.com/start.png",
        "shot_type": "customize",
        "end_image_url": None,
        "multi_prompt": None,
        "duration": "5",
        "generate_audio": False,
    }


def test_kling_o3_4k_image_to_video_accepts_end_frame_and_multi_prompt() -> None:
    config = KlingVideoO34kImageToVideoConfig(
        app_id="fal-ai/kling-video/o3/4k/image-to-video",
        image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
        multi_prompt=[
            KlingO3MultiPromptElement(prompt="First shot.", duration="3"),
            KlingO3MultiPromptElement(prompt="Second shot.", duration="5"),
        ],
        duration="8",
        generate_audio=True,
        shot_type="intelligent",
    )

    assert config.app_id == "fal-ai/kling-video/o3/4k/image-to-video"
    assert config.prompt is None
    assert config.end_image_url == "https://example.com/end.png"
    assert config.duration == "8"
    assert config.generate_audio is True


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
                "prompt": "Move gently.",
            },
            "image_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
                "image_url": "https://example.com/start.png",
            },
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
                "prompt": "Move gently.",
                "multi_prompt": [{"prompt": "Second shot."}],
                "image_url": "https://example.com/start.png",
            },
            "not both",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
                "prompt": "Move gently.",
                "image_url": "https://example.com/start.png",
                "duration": "16",
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/image-to-video",
                "prompt": "Move gently.",
                "image_url": "https://example.com/start.png",
                "shot_type": "manual",
            },
            "shot_type",
        ),
    ],
)
def test_kling_o3_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoO3ProImageToVideoConfig.model_validate(payload)
