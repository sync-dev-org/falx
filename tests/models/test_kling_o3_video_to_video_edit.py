from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import KlingO3ImageElementInput, KlingVideoO3ProVideoToVideoEditConfig


def test_kling_o3_pro_video_to_video_edit_accepts_schema_defaults() -> None:
    config = KlingVideoO3ProVideoToVideoEditConfig(
        app_id="fal-ai/kling-video/o3/pro/video-to-video/edit",
        prompt="Change environment to snow.",
        video_url="https://example.com/reference.mp4",
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
        "prompt": "Change environment to snow.",
        "video_url": "https://example.com/reference.mp4",
        "shot_type": "customize",
        "elements": None,
        "keep_audio": True,
        "image_urls": None,
    }


def test_kling_o3_pro_video_to_video_edit_accepts_elements_and_image_refs() -> None:
    config = KlingVideoO3ProVideoToVideoEditConfig(
        app_id="fal-ai/kling-video/o3/pro/video-to-video/edit",
        prompt="Replace animal with @Element1 and match @Image2.",
        video_url="https://example.com/reference.mov",
        elements=[
            KlingO3ImageElementInput(
                frontal_image_url="https://example.com/front.png",
                reference_image_urls=["https://example.com/side.png"],
            )
        ],
        keep_audio=False,
        image_urls=["https://example.com/ref-1.png", "https://example.com/ref-2.png"],
    )

    assert config.keep_audio is False
    assert len(config.elements or []) == 1
    assert len(config.image_urls or []) == 2


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "video_url": "https://example.com/reference.mp4",
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "prompt": "Edit the clip.",
            },
            "video_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "prompt": "Edit the clip.",
                "video_url": "https://example.com/reference.mp4",
                "shot_type": "intelligent",
            },
            "customize",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "prompt": "Show @Element1.",
                "video_url": "https://example.com/reference.mp4",
                "elements": [{}],
            },
            "frontal_image_url or reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "prompt": "Show @Element2.",
                "video_url": "https://example.com/reference.mp4",
                "elements": [{"frontal_image_url": "https://example.com/front.png"}],
            },
            "@Element2",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "prompt": "Show @Image2.",
                "video_url": "https://example.com/reference.mp4",
                "image_urls": ["https://example.com/ref-1.png"],
            },
            "@Image2",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/o3/pro/video-to-video/edit",
                "prompt": "Edit the clip.",
                "video_url": "https://example.com/reference.mp4",
                "elements": [{"frontal_image_url": "https://example.com/front.png"}],
                "image_urls": [
                    "https://example.com/ref-1.png",
                    "https://example.com/ref-2.png",
                    "https://example.com/ref-3.png",
                    "https://example.com/ref-4.png",
                ],
            },
            "Maximum 4 total",
        ),
    ],
)
def test_kling_o3_pro_video_to_video_edit_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoO3ProVideoToVideoEditConfig.model_validate(payload)
