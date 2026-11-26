from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    KlingV3ComboElementInput,
    KlingV3MultiPromptElement,
    KlingVideoV3ProImageToVideoConfig,
)


def test_kling_v3_pro_image_to_video_accepts_minimal_prompt_request() -> None:
    config = KlingVideoV3ProImageToVideoConfig(
        app_id="fal-ai/kling-video/v3/pro/image-to-video",
        prompt="The subject slowly turns toward the camera.",
        start_image_url="https://example.com/start.png",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
        "prompt": "The subject slowly turns toward the camera.",
        "multi_prompt": None,
        "start_image_url": "https://example.com/start.png",
        "duration": "5",
        "generate_audio": True,
        "end_image_url": None,
        "elements": None,
        "shot_type": "customize",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
    }


def test_kling_v3_pro_image_to_video_accepts_multi_prompt_and_elements() -> None:
    config = KlingVideoV3ProImageToVideoConfig(
        app_id="fal-ai/kling-video/v3/pro/image-to-video",
        multi_prompt=[
            KlingV3MultiPromptElement(prompt="@Element1 enters the room.", duration="4"),
            KlingV3MultiPromptElement(prompt="@Element2 looks up.", duration="6"),
        ],
        start_image_url="https://example.com/start.png",
        duration="10",
        generate_audio=False,
        end_image_url="https://example.com/end.png",
        elements=[
            KlingV3ComboElementInput(
                frontal_image_url="https://example.com/character-front.png",
                reference_image_urls=["https://example.com/character-side.png"],
            ),
            KlingV3ComboElementInput(video_url="https://example.com/prop.mp4", voice_id="voice_1"),
        ],
        shot_type="intelligent",
        negative_prompt="low detail",
        cfg_scale=1.0,
    )

    assert config.duration == "10"
    assert config.generate_audio is False
    assert config.shot_type == "intelligent"
    assert config.cfg_scale == 1.0
    assert len(config.elements or []) == 2


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
            },
            "start_image_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "start_image_url": "https://example.com/start.png",
            },
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "multi_prompt": [{"prompt": "Second shot."}],
                "start_image_url": "https://example.com/start.png",
            },
            "not both",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "x" * 2501,
                "start_image_url": "https://example.com/start.png",
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "duration": "2",
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "shot_type": "manual",
            },
            "shot_type",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "cfg_scale": 1.1,
            },
            "cfg_scale",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "multi_prompt": [{"duration": "5"}],
                "start_image_url": "https://example.com/start.png",
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "multi_prompt": [{"prompt": "Shot.", "duration": "16"}],
                "start_image_url": "https://example.com/start.png",
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Show @Element2.",
                "start_image_url": "https://example.com/start.png",
                "elements": [{"frontal_image_url": "https://example.com/character.png"}],
            },
            "@Element2",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "elements": [
                    {
                        "frontal_image_url": "https://example.com/character.png",
                        "video_url": "https://example.com/clip.mp4",
                    }
                ],
            },
            "either image fields or video_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "elements": [
                    {
                        "voice_id": "voice_1",
                        "frontal_image_url": "https://example.com/character.png",
                    }
                ],
            },
            "voice_id requires video_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "elements": [{"reference_image_urls": []}],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "elements": [{"reference_image_urls": ["1", "2", "3", "4"]}],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/pro/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "elements": [
                    {"video_url": "https://example.com/clip-1.mp4"},
                    {"video_url": "https://example.com/clip-2.mp4"},
                ],
            },
            "one element with a video",
        ),
    ],
)
def test_kling_v3_pro_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoV3ProImageToVideoConfig.model_validate(payload)
