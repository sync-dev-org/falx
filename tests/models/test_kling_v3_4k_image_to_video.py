from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import KlingVideoV34kImageToVideoConfig


def test_kling_v3_4k_image_to_video_accepts_schema_defaults() -> None:
    config = KlingVideoV34kImageToVideoConfig(
        app_id="fal-ai/kling-video/v3/4k/image-to-video",
        prompt="The subject walks through a sunlit hall.",
        start_image_url="https://example.com/start.png",
    )

    assert config.duration == "5"
    assert config.generate_audio is True
    assert config.shot_type == "customize"
    assert config.negative_prompt == "blur, distort, and low quality"
    assert config.cfg_scale == 0.5


def test_kling_v3_4k_image_to_video_accepts_4k_app_id_and_end_frame() -> None:
    config = KlingVideoV34kImageToVideoConfig(
        app_id="fal-ai/kling-video/v3/4k/image-to-video",
        prompt="The camera completes on the final pose.",
        start_image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
        duration="15",
    )

    assert config.app_id == "fal-ai/kling-video/v3/4k/image-to-video"
    assert config.end_image_url == "https://example.com/end.png"
    assert config.duration == "15"


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/image-to-video",
                "prompt": "Move gently.",
            },
            "start_image_url",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/image-to-video",
                "start_image_url": "https://example.com/start.png",
            },
            "prompt or multi_prompt",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/image-to-video",
                "prompt": "Move gently.",
                "multi_prompt": [{"prompt": "Second shot."}],
                "start_image_url": "https://example.com/start.png",
            },
            "not both",
        ),
        (
            {
                "app_id": "fal-ai/kling-video/v3/4k/image-to-video",
                "prompt": "Move gently.",
                "start_image_url": "https://example.com/start.png",
                "duration": "10",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_kling_v3_4k_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoV34kImageToVideoConfig.model_validate(payload)
