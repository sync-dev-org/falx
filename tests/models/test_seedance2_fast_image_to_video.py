from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Seedance2FastImageToVideoConfig


def test_seedance2_fast_image_to_video_config_accepts_minimal_required_fields() -> None:
    config = Seedance2FastImageToVideoConfig(
        app_id="bytedance/seedance-2.0/fast/image-to-video",
        prompt="The camera slowly pushes in as clouds drift across the city skyline.",
        image_url="https://example.com/start.png",
    )

    assert config.prompt == "The camera slowly pushes in as clouds drift across the city skyline."
    assert config.image_url == "https://example.com/start.png"
    assert config.end_image_url is None
    assert config.resolution == "720p"
    assert config.duration == "auto"
    assert config.aspect_ratio == "auto"
    assert config.generate_audio is True
    assert config.bitrate_mode == "standard"
    assert config.codec == "auto"
    assert config.return_last_frame is False
    assert config.end_user_id is None


def test_seedance2_fast_image_to_video_config_accepts_all_fast_tier_fields() -> None:
    config = Seedance2FastImageToVideoConfig(
        app_id="bytedance/seedance-2.0/fast/image-to-video",
        prompt="The sun sets behind the mountains, sky shifting from gold to deep purple.",
        image_url="https://example.com/start.webp",
        end_image_url="https://example.com/end.webp",
        resolution="720p",
        duration="8",
        aspect_ratio="16:9",
        generate_audio=False,
        bitrate_mode="high",
        codec="H265",
        return_last_frame=True,
        end_user_id="user-123",
    )

    assert config.model_dump() == {
        "app_id": "bytedance/seedance-2.0/fast/image-to-video",
        "prompt": "The sun sets behind the mountains, sky shifting from gold to deep purple.",
        "image_url": "https://example.com/start.webp",
        "end_image_url": "https://example.com/end.webp",
        "resolution": "720p",
        "duration": "8",
        "aspect_ratio": "16:9",
        "generate_audio": False,
        "bitrate_mode": "high",
        "codec": "H265",
        "return_last_frame": True,
        "end_user_id": "user-123",
    }


@pytest.mark.parametrize("resolution", ["480p", "720p"])
def test_seedance2_fast_image_to_video_config_accepts_fast_tier_resolutions(
    resolution: str,
) -> None:
    config = Seedance2FastImageToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/image-to-video",
            "prompt": "Animate the still image with a slow dolly move.",
            "image_url": "https://example.com/start.jpg",
            "resolution": resolution,
        }
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("duration", ["auto", *(str(value) for value in range(4, 16))])
def test_seedance2_fast_image_to_video_config_accepts_duration_enum(
    duration: str,
) -> None:
    config = Seedance2FastImageToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/image-to-video",
            "prompt": "Animate the still image with a slow tracking shot.",
            "image_url": "https://example.com/start.jpg",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize("bitrate_mode", ["standard", "high"])
def test_seedance2_fast_image_to_video_config_accepts_bitrate_mode_enum(
    bitrate_mode: str,
) -> None:
    config = Seedance2FastImageToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/image-to-video",
            "prompt": "Animate the still image with a slow tracking shot.",
            "image_url": "https://example.com/start.jpg",
            "bitrate_mode": bitrate_mode,
        }
    )

    assert config.bitrate_mode == bitrate_mode


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "image_url": "https://example.com/start.jpg",
            },
            "prompt",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
            },
            "image_url",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "resolution": "1080p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "duration": "3",
            },
            "duration",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "duration": "16",
            },
            "duration",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "aspect_ratio": "2:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "bitrate_mode": "lossless",
            },
            "bitrate_mode",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/image-to-video",
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.jpg",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_seedance2_fast_image_to_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Seedance2FastImageToVideoConfig.model_validate(payload)
