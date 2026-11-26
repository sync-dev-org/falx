from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Seedance2FastReferenceToVideoConfig, validate_parameters


def test_seedance2_fast_reference_to_video_config_accepts_full_config() -> None:
    config = Seedance2FastReferenceToVideoConfig(
        app_id="bytedance/seedance-2.0/fast/reference-to-video",
        prompt="Use @Image1 as the hero and @Video1 as the movement reference.",
        image_urls=["https://example.com/hero.png"],
        video_urls=["https://example.com/motion.mp4"],
        audio_urls=["https://example.com/music.mp3"],
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
        "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
        "prompt": "Use @Image1 as the hero and @Video1 as the movement reference.",
        "image_urls": ["https://example.com/hero.png"],
        "video_urls": ["https://example.com/motion.mp4"],
        "audio_urls": ["https://example.com/music.mp3"],
        "resolution": "720p",
        "duration": "8",
        "aspect_ratio": "16:9",
        "generate_audio": False,
        "bitrate_mode": "high",
        "codec": "H265",
        "return_last_frame": True,
        "end_user_id": "user-123",
    }


def test_seedance2_fast_reference_to_video_config_routes_through_registered_validator() -> None:
    validated = validate_parameters(
        "bytedance/seedance-2.0/fast/reference-to-video",
        {
            "prompt": "Animate @Image1 with the camera rhythm from @Video1.",
            "image_urls": ["https://example.com/hero.png"],
            "video_urls": ["https://example.com/motion.mp4"],
        },
    )

    assert isinstance(validated, Seedance2FastReferenceToVideoConfig)


def test_seedance2_fast_reference_to_video_config_accepts_reference_url_lists() -> None:
    config = Seedance2FastReferenceToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
            "prompt": "Blend @Image1 and @Image2, then time the edit to @Audio1.",
            "image_urls": [
                "https://example.com/hero.png",
                "https://example.com/style.png",
            ],
            "video_urls": ["https://example.com/motion.mp4"],
            "audio_urls": ["https://example.com/music.mp3"],
        }
    )

    assert config.image_urls == [
        "https://example.com/hero.png",
        "https://example.com/style.png",
    ]
    assert config.video_urls == ["https://example.com/motion.mp4"]
    assert config.audio_urls == ["https://example.com/music.mp3"]


def test_seedance2_fast_reference_to_video_config_uses_documented_defaults() -> None:
    config = Seedance2FastReferenceToVideoConfig(
        app_id="bytedance/seedance-2.0/fast/reference-to-video",
        prompt="Generate a cinematic transition from the references.",
    )

    assert config.image_urls == []
    assert config.video_urls == []
    assert config.audio_urls == []
    assert config.resolution == "720p"
    assert config.duration == "auto"
    assert config.aspect_ratio == "auto"
    assert config.generate_audio is True
    assert config.bitrate_mode == "standard"
    assert config.codec == "auto"
    assert config.return_last_frame is False
    assert config.end_user_id is None


@pytest.mark.parametrize("resolution", ["480p", "720p"])
def test_seedance2_fast_reference_to_video_config_accepts_fast_tier_resolutions(
    resolution: str,
) -> None:
    config = Seedance2FastReferenceToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
            "prompt": "Animate @Image1 with a slow push-in.",
            "image_urls": ["https://example.com/image.png"],
            "resolution": resolution,
        }
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("bitrate_mode", ["standard", "high"])
def test_seedance2_fast_reference_to_video_config_accepts_bitrate_mode_enum(
    bitrate_mode: str,
) -> None:
    config = Seedance2FastReferenceToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
            "prompt": "Animate @Image1 through a smooth push-in.",
            "image_urls": ["https://example.com/image.png"],
            "bitrate_mode": bitrate_mode,
        }
    )

    assert config.bitrate_mode == bitrate_mode


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
            },
            "prompt",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Animate the references.",
                "unexpected": True,
            },
            "unexpected",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Animate @Image1 through @Image10.",
                "image_urls": [f"https://example.com/image-{index}.png" for index in range(10)],
            },
            "image_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Animate with too many video references.",
                "video_urls": [f"https://example.com/video-{index}.mp4" for index in range(4)],
            },
            "video_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Animate with too many audio references.",
                "image_urls": ["https://example.com/image.png"],
                "audio_urls": [f"https://example.com/audio-{index}.mp3" for index in range(4)],
            },
            "audio_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Animate with too many total references.",
                "image_urls": [f"https://example.com/image-{index}.png" for index in range(9)],
                "video_urls": [f"https://example.com/video-{index}.mp4" for index in range(3)],
                "audio_urls": ["https://example.com/audio.mp3"],
            },
            "total files",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Generate audio-only reference motion.",
                "audio_urls": ["https://example.com/audio.mp3"],
            },
            "audio_urls require image_urls or video_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Reject null image references before submit.",
                "image_urls": None,
            },
            "image_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Reject null video references before submit.",
                "video_urls": None,
            },
            "video_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Reject null audio references before submit.",
                "audio_urls": None,
            },
            "audio_urls",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Reject unsupported 1080p resolution.",
                "resolution": "1080p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Reject unsupported 4k resolution.",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
                "prompt": "Reject unsupported bitrate modes.",
                "bitrate_mode": "lossless",
            },
            "bitrate_mode",
        ),
    ],
)
def test_seedance2_fast_reference_to_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Seedance2FastReferenceToVideoConfig.model_validate(payload)


def test_seedance2_fast_reference_to_video_config_accepts_reference_boundaries() -> None:
    config = Seedance2FastReferenceToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
            "prompt": "Use the full supported reference budget.",
            "image_urls": [f"https://example.com/image-{index}.png" for index in range(9)],
            "video_urls": [f"https://example.com/video-{index}.mp4" for index in range(3)],
        }
    )

    assert len(config.image_urls or []) == 9
    assert len(config.video_urls or []) == 3


def test_seedance2_fast_reference_to_video_config_accepts_audio_with_visual_reference() -> None:
    config = Seedance2FastReferenceToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/fast/reference-to-video",
            "prompt": "Use @Image1 and pace the movement to @Audio1.",
            "image_urls": ["https://example.com/image.png"],
            "audio_urls": ["https://example.com/audio.mp3"],
        }
    )

    assert config.audio_urls == ["https://example.com/audio.mp3"]
