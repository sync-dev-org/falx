from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Seedance2MiniTextToVideoConfig


def test_seedance2_mini_text_to_video_config_accepts_minimal_required_fields() -> None:
    config = Seedance2MiniTextToVideoConfig(
        app_id="bytedance/seedance-2.0/mini/text-to-video",
        prompt="The camera slowly pushes in as clouds drift across the city skyline.",
    )

    assert config.prompt == "The camera slowly pushes in as clouds drift across the city skyline."
    assert config.resolution == "720p"
    assert config.duration == "auto"
    assert config.aspect_ratio == "auto"
    assert config.generate_audio is True
    assert config.codec == "auto"
    assert config.return_last_frame is False
    assert config.end_user_id is None


def test_seedance2_mini_text_to_video_config_accepts_all_mini_tier_fields() -> None:
    config = Seedance2MiniTextToVideoConfig(
        app_id="bytedance/seedance-2.0/mini/text-to-video",
        prompt="The sun sets behind the mountains, sky shifting from gold to deep purple.",
        resolution="720p",
        duration="8",
        aspect_ratio="16:9",
        generate_audio=False,
        codec="H265",
        return_last_frame=True,
        end_user_id="user-123",
    )

    assert config.model_dump() == {
        "app_id": "bytedance/seedance-2.0/mini/text-to-video",
        "prompt": "The sun sets behind the mountains, sky shifting from gold to deep purple.",
        "resolution": "720p",
        "duration": "8",
        "aspect_ratio": "16:9",
        "generate_audio": False,
        "codec": "H265",
        "return_last_frame": True,
        "end_user_id": "user-123",
    }


@pytest.mark.parametrize("resolution", ["480p", "720p"])
def test_seedance2_mini_text_to_video_config_accepts_mini_tier_resolutions(
    resolution: str,
) -> None:
    config = Seedance2MiniTextToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/mini/text-to-video",
            "prompt": "A cinematic city street slowly fills with morning light.",
            "resolution": resolution,
        }
    )

    assert config.resolution == resolution


@pytest.mark.parametrize("duration", ["auto", *(str(value) for value in range(4, 16))])
def test_seedance2_mini_text_to_video_config_accepts_duration_enum(
    duration: str,
) -> None:
    config = Seedance2MiniTextToVideoConfig.model_validate(
        {
            "app_id": "bytedance/seedance-2.0/mini/text-to-video",
            "prompt": "A dancer moves through a neon-lit rainstorm.",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
            },
            "prompt",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "resolution": "1080p",
            },
            "resolution",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "duration": "3",
            },
            "duration",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "duration": "16",
            },
            "duration",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "aspect_ratio": "2:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "bitrate_mode": "high",
            },
            "bitrate_mode",
        ),
        (
            {
                "app_id": "bytedance/seedance-2.0/mini/text-to-video",
                "prompt": "A glowing train crosses a bridge at night.",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_seedance2_mini_text_to_video_config_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Seedance2MiniTextToVideoConfig.model_validate(payload)
