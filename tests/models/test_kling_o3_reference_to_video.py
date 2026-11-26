from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    KlingO3ComboElementInput,
    KlingO3MultiPromptElement,
    KlingVideoO3ProReferenceToVideoConfig,
    KlingVideoO34kReferenceToVideoConfig,
)


def test_kling_o3_pro_reference_to_video_accepts_elements_and_image_refs() -> None:
    config = KlingVideoO3ProReferenceToVideoConfig(
        app_id="fal-ai/kling-video/o3/pro/reference-to-video",
        prompt="@Element1 enters the scene with @Image1 styling.",
        start_image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
        elements=[
            KlingO3ComboElementInput(
                frontal_image_url="https://example.com/front.png",
                reference_image_urls=["https://example.com/side.png"],
            )
        ],
        image_urls=["https://example.com/style.png"],
        duration="8",
        generate_audio=True,
        aspect_ratio="1:1",
        shot_type="intelligent",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
        "prompt": "@Element1 enters the scene with @Image1 styling.",
        "start_image_url": "https://example.com/start.png",
        "duration": "8",
        "end_image_url": "https://example.com/end.png",
        "generate_audio": True,
        "aspect_ratio": "1:1",
        "shot_type": "intelligent",
        "elements": [
            {
                "reference_image_urls": ["https://example.com/side.png"],
                "video_url": None,
                "voice_id": None,
                "frontal_image_url": "https://example.com/front.png",
            }
        ],
        "image_urls": ["https://example.com/style.png"],
        "multi_prompt": None,
    }


def test_kling_o3_4k_reference_to_video_accepts_seven_total_references() -> None:
    config = KlingVideoO34kReferenceToVideoConfig(
        app_id="fal-ai/kling-video/o3/4k/reference-to-video",
        multi_prompt=[KlingO3MultiPromptElement(prompt="@Element1 meets @Image6.", duration="5")],
        elements=[KlingO3ComboElementInput(video_url="https://example.com/actor.mp4")],
        image_urls=[f"https://example.com/ref-{index}.png" for index in range(1, 7)],
    )

    assert config.app_id == "fal-ai/kling-video/o3/4k/reference-to-video"
    assert len(config.image_urls or []) == 6


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {"app_id": "fal-ai/kling-video/o3/pro/reference-to-video"},
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Show @Element2.",
                "elements": [{"frontal_image_url": "https://example.com/front.png"}],
            },
            "@Element2",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Show @Image2.",
                "image_urls": ["https://example.com/style.png"],
            },
            "@Image2",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Move gently.",
                "elements": [
                    {
                        "frontal_image_url": "https://example.com/front.png",
                        "video_url": "https://example.com/clip.mp4",
                    }
                ],
            },
            "either image fields or video_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Move gently.",
                "elements": [
                    {
                        "voice_id": "voice_1",
                        "frontal_image_url": "https://example.com/front.png",
                    }
                ],
            },
            "voice_id requires video_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Move gently.",
                "elements": [{"reference_image_urls": []}],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Move gently.",
                "elements": [{"reference_image_urls": ["1", "2", "3", "4"]}],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Move gently.",
                "elements": [
                    {"video_url": "https://example.com/clip-1.mp4"},
                    {"video_url": "https://example.com/clip-2.mp4"},
                ],
            },
            "one element with a video",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/reference-to-video",
                "prompt": "Move gently.",
                "elements": [{"video_url": "https://example.com/clip.mp4"}],
                "image_urls": [
                    "https://example.com/ref-1.png",
                    "https://example.com/ref-2.png",
                    "https://example.com/ref-3.png",
                    "https://example.com/ref-4.png",
                ],
            },
            "Maximum 4 total",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/4k/reference-to-video",
                "prompt": "Move gently.",
                "image_urls": [
                    "https://example.com/ref-1.png",
                    "https://example.com/ref-2.png",
                    "https://example.com/ref-3.png",
                    "https://example.com/ref-4.png",
                    "https://example.com/ref-5.png",
                    "https://example.com/ref-6.png",
                    "https://example.com/ref-7.png",
                    "https://example.com/ref-8.png",
                ],
            },
            "Maximum 7 total",
        ),
    ],
)
def test_kling_o3_reference_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    cls = (
        KlingVideoO34kReferenceToVideoConfig
        if payload["app_id"] == "fal-ai/kling-video/o3/4k/reference-to-video"
        else KlingVideoO3ProReferenceToVideoConfig
    )
    with pytest.raises(ValidationError, match=needle):
        cls.model_validate(payload)
