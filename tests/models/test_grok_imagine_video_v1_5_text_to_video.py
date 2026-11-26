from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    GrokImagineVideoV15TextToVideoConfig,
    config_class_for_app_id,
)

APP_ID = "xai/grok-imagine-video/v1.5/text-to-video"
ASPECT_RATIOS = ["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "21:9", "5:2"]


def test_grok_imagine_video_v1_5_text_to_video_accepts_schema_defaults() -> None:
    config = GrokImagineVideoV15TextToVideoConfig(
        app_id=APP_ID,
        prompt="A knight walks through a mystical forest.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A knight walks through a mystical forest.",
        "duration": 6,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "generate_audio": None,
        "enable_safety_checker": True,
    }


def test_grok_imagine_video_v1_5_text_to_video_accepts_all_fields() -> None:
    config = GrokImagineVideoV15TextToVideoConfig(
        app_id=APP_ID,
        prompt="A knight walks through a mystical forest.",
        duration=15,
        resolution="1080p",
        aspect_ratio="9:16",
        generate_audio=False,
        enable_safety_checker=False,
    )

    assert config.duration == 15
    assert config.resolution == "1080p"
    assert config.aspect_ratio == "9:16"
    assert config.generate_audio is False
    assert config.enable_safety_checker is False


@pytest.mark.parametrize("generate_audio", [None, False, True])
def test_grok_imagine_video_v1_5_text_to_video_accepts_optional_audio(
    generate_audio: bool | None,
) -> None:
    config = GrokImagineVideoV15TextToVideoConfig(
        app_id=APP_ID,
        prompt="A cinematic scene.",
        generate_audio=generate_audio,
    )

    assert config.generate_audio is generate_audio
    payload = config.model_dump(exclude={"app_id"}, exclude_none=True)
    if generate_audio is None:
        assert "generate_audio" not in payload
    else:
        assert payload["generate_audio"] is generate_audio


@pytest.mark.parametrize("aspect_ratio", ASPECT_RATIOS)
def test_grok_imagine_video_v1_5_text_to_video_accepts_aspect_ratio_enum(
    aspect_ratio: str,
) -> None:
    config = GrokImagineVideoV15TextToVideoConfig(
        app_id=APP_ID,
        prompt="A cinematic scene.",
        aspect_ratio=aspect_ratio,
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p"])
@pytest.mark.parametrize("duration", [1, 15])
def test_grok_imagine_video_v1_5_text_to_video_accepts_enums_and_boundaries(
    resolution: str,
    duration: int,
) -> None:
    config = GrokImagineVideoV15TextToVideoConfig(
        app_id=APP_ID,
        prompt="A cinematic scene.",
        resolution=resolution,
        duration=duration,
    )

    assert config.resolution == resolution
    assert config.duration == duration


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": "x" * 4097}, "prompt"),
        ({"prompt": "A scene.", "aspect_ratio": "auto"}, "aspect_ratio"),
        ({"prompt": "A scene.", "resolution": "4k"}, "resolution"),
        ({"prompt": "A scene.", "duration": 0}, "duration"),
        ({"prompt": "A scene.", "duration": 16}, "duration"),
        ({"prompt": "A scene.", "generate_audio": "invalid"}, "generate_audio"),
        ({"prompt": "A scene.", "enable_safety_checker": None}, "enable_safety_checker"),
        ({"prompt": "A scene.", "unexpected": True}, "unexpected"),
    ],
)
def test_grok_imagine_video_v1_5_text_to_video_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineVideoV15TextToVideoConfig.model_validate({"app_id": APP_ID, **parameters})


def test_grok_imagine_video_v1_5_text_to_video_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is GrokImagineVideoV15TextToVideoConfig
    assert GrokImagineVideoV15TextToVideoConfig.random_seed_field is None
