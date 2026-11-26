from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    GrokImagineVideoV15ImageToVideoConfig,
    config_class_for_app_id,
)

APP_ID = "xai/grok-imagine-video/v1.5/image-to-video"


def test_grok_imagine_video_v1_5_image_to_video_accepts_schema_defaults() -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="The subject slowly turns toward the camera.",
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "The subject slowly turns toward the camera.",
        "image_url": "https://example.com/source.png",
        "duration": 6,
        "resolution": "720p",
        "generate_audio": None,
        "enable_safety_checker": True,
        "end_image_url": None,
        "keyframes": None,
    }


def test_grok_imagine_video_v1_5_image_to_video_accepts_all_fields() -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="The subject slowly turns toward the camera.",
        image_url="https://example.com/source.png",
        duration=15,
        resolution="1080p",
        generate_audio=False,
        enable_safety_checker=False,
    )

    assert config.duration == 15
    assert config.resolution == "1080p"
    assert config.generate_audio is False
    assert config.enable_safety_checker is False


@pytest.mark.parametrize("generate_audio", [None, False, True])
def test_grok_imagine_video_v1_5_image_to_video_accepts_optional_audio(
    generate_audio: bool | None,
) -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="Animate the subject.",
        image_url="https://example.com/start.png",
        generate_audio=generate_audio,
    )

    assert config.generate_audio is generate_audio
    payload = config.model_dump(exclude={"app_id"}, exclude_none=True)
    if generate_audio is None:
        assert "generate_audio" not in payload
    else:
        assert payload["generate_audio"] is generate_audio


@pytest.mark.parametrize("frame_count", [0, 1, 4])
def test_grok_imagine_video_v1_5_image_to_video_serializes_optional_anchors(
    frame_count: int,
) -> None:
    frames = [
        {"image_url": f"https://example.com/{index}.png", "timestamp": index + 0.5}
        for index in range(frame_count)
    ]
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="Move between anchors.",
        image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
        keyframes=frames,
    )

    payload = config.model_dump(exclude={"app_id"}, exclude_none=True)
    assert payload["end_image_url"] == "https://example.com/end.png"
    assert payload["keyframes"] == frames


@pytest.mark.parametrize(
    ("frames", "needle"),
    [
        ([{"image_url": "https://example.com/a.png", "timestamp": 0}], "timestamp"),
        ([{"image_url": "https://example.com/a.png", "timestamp": -0.1}], "timestamp"),
        ([{"image_url": "https://example.com/a.png", "timestamp": 6}], "duration"),
        ([{"image_url": "https://example.com/a.png", "timestamp": 6.1}], "duration"),
        ([{"image_url": "https://example.com/a.png", "timestamp": 1}] * 5, "keyframes"),
        ([{"image_url": "https://example.com/a.png"}], "timestamp"),
        ([{"timestamp": 1}], "image_url"),
        ([{"image_url": "https://example.com/a.png", "timestamp": 1, "extra": 1}], "extra"),
    ],
)
def test_grok_imagine_video_v1_5_image_to_video_rejects_invalid_anchors(
    frames: list[dict[str, object]],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineVideoV15ImageToVideoConfig(
            app_id=APP_ID,
            prompt="Move between anchors.",
            image_url="https://example.com/start.png",
            keyframes=frames,
        )


def test_grok_imagine_video_v1_5_image_to_video_uses_requested_duration_for_anchors() -> None:
    with pytest.raises(ValidationError, match="duration"):
        GrokImagineVideoV15ImageToVideoConfig(
            app_id=APP_ID,
            prompt="Move between anchors.",
            image_url="https://example.com/start.png",
            duration=1,
            keyframes=[{"image_url": "https://example.com/a.png", "timestamp": 1}],
        )


@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p"])
@pytest.mark.parametrize("duration", [1, 15])
def test_grok_imagine_video_v1_5_image_to_video_accepts_enums_and_boundaries(
    resolution: str,
    duration: int,
) -> None:
    config = GrokImagineVideoV15ImageToVideoConfig(
        app_id=APP_ID,
        prompt="Animate the subject.",
        image_url="https://example.com/source.png",
        resolution=resolution,
        duration=duration,
    )

    assert config.resolution == resolution
    assert config.duration == duration


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"image_url": "https://example.com/source.png"}, "prompt"),
        ({"prompt": "Animate the subject."}, "image_url"),
        (
            {
                "prompt": "x" * 4097,
                "image_url": "https://example.com/source.png",
            },
            "prompt",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "duration": 0,
            },
            "duration",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "aspect_ratio": "16:9",
            },
            "aspect_ratio",
        ),
        (
            {
                "prompt": "Animate the subject.",
                "image_url": "https://example.com/source.png",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_grok_imagine_video_v1_5_image_to_video_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineVideoV15ImageToVideoConfig.model_validate({"app_id": APP_ID, **parameters})


def test_grok_imagine_video_v1_5_image_to_video_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is GrokImagineVideoV15ImageToVideoConfig
    assert GrokImagineVideoV15ImageToVideoConfig.random_seed_field is None
