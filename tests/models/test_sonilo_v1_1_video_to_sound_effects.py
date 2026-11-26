from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SoniloV11SfxSegment,
    SoniloV11VideoToSoundEffectsConfig,
)

APP_ID = "sonilo/v1.1/video-to-sound-effects"


def test_sonilo_v1_1_video_to_sound_effects_accepts_schema_defaults() -> None:
    config = SoniloV11VideoToSoundEffectsConfig(
        app_id=APP_ID,
        video_url="https://example.com/source.mp4",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "video_url": "https://example.com/source.mp4",
        "prompt": None,
        "segments": None,
        "audio_format": "aac",
    }


def test_sonilo_v1_1_video_to_sound_effects_accepts_all_fields() -> None:
    config = SoniloV11VideoToSoundEffectsConfig(
        app_id=APP_ID,
        video_url="https://example.com/source.mp4",
        prompt="Natural foley and a light breeze.",
        segments=[
            {"start": 0, "end": 2.5, "prompt": "Footsteps on gravel."},
            {"start": 2.5, "end": 5, "prompt": "A wooden door closes."},
        ],
        audio_format="flac",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "video_url": "https://example.com/source.mp4",
        "prompt": "Natural foley and a light breeze.",
        "segments": [
            {"start": 0.0, "end": 2.5, "prompt": "Footsteps on gravel."},
            {"start": 2.5, "end": 5.0, "prompt": "A wooden door closes."},
        ],
        "audio_format": "flac",
    }


def test_sonilo_v1_1_sfx_segment_accepts_schema_defaults() -> None:
    segment = SoniloV11SfxSegment()

    assert segment.model_dump() == {"start": 0.0, "end": 0.0, "prompt": ""}


def test_sonilo_v1_1_schema_matches_openapi_contract() -> None:
    schema = SoniloV11VideoToSoundEffectsConfig.model_json_schema()
    segment_schema = schema["$defs"]["SoniloV11SfxSegment"]

    assert schema["required"] == ["app_id", "video_url"]
    assert schema["properties"]["audio_format"]["default"] == "aac"
    assert schema["properties"]["audio_format"]["enum"] == ["wav", "mp3", "aac", "flac"]
    assert schema["properties"]["audio_format"]["description"] == (
        "Format of the returned audio file: aac (default), mp3, wav, or flac. "
        "(The video with sound is always AAC.)"
    )
    assert schema["properties"]["segments"]["anyOf"][0]["items"] == {
        "$ref": "#/$defs/SoniloV11SfxSegment"
    }
    assert "required" not in segment_schema
    assert segment_schema["properties"]["start"]["default"] == 0.0
    assert segment_schema["properties"]["start"]["minimum"] == 0
    assert segment_schema["properties"]["start"]["description"] == (
        "Segment start time in seconds (from video start). The FIRST segment's start must be 0."
    )
    assert segment_schema["properties"]["end"]["default"] == 0.0
    assert segment_schema["properties"]["end"]["minimum"] == 0
    assert segment_schema["properties"]["end"]["description"] == (
        "Segment end time in seconds. Must equal the next segment's start (contiguous; "
        "no gaps/overlaps); the last segment's end must be <= the video duration."
    )
    assert segment_schema["properties"]["prompt"]["default"] == ""


def test_sonilo_v1_1_accepts_explicit_null_optional_fields() -> None:
    config = SoniloV11VideoToSoundEffectsConfig(
        app_id=APP_ID,
        video_url="https://example.com/source.mp4",
        prompt=None,
        segments=None,
    )

    assert config.prompt is None
    assert config.segments is None


def test_sonilo_v1_1_accepts_empty_segments() -> None:
    config = SoniloV11VideoToSoundEffectsConfig(
        app_id=APP_ID,
        video_url="https://example.com/source.mp4",
        segments=[],
    )

    assert config.segments == []


@pytest.mark.parametrize("audio_format", ["wav", "mp3", "aac", "flac"])
def test_sonilo_v1_1_accepts_audio_format_enum(audio_format: str) -> None:
    config = SoniloV11VideoToSoundEffectsConfig(
        app_id=APP_ID,
        video_url="https://example.com/source.mp4",
        audio_format=audio_format,
    )

    assert config.audio_format == audio_format


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "video_url"),
        ({"app_id": APP_ID, "video_url": None}, "video_url"),
        (
            {
                "app_id": APP_ID,
                "video_url": "https://example.com/source.mp4",
                "audio_format": "ogg",
            },
            "audio_format",
        ),
        (
            {
                "app_id": APP_ID,
                "video_url": "https://example.com/source.mp4",
                "segments": [{"start": -0.1}],
            },
            "start",
        ),
        (
            {
                "app_id": APP_ID,
                "video_url": "https://example.com/source.mp4",
                "segments": [{"end": -0.1}],
            },
            "end",
        ),
        (
            {
                "app_id": APP_ID,
                "video_url": "https://example.com/source.mp4",
                "segments": [{"prompt": None}],
            },
            "prompt",
        ),
        (
            {
                "app_id": APP_ID,
                "video_url": "https://example.com/source.mp4",
                "segments": [{"unexpected": True}],
            },
            "unexpected",
        ),
        (
            {
                "app_id": APP_ID,
                "video_url": "https://example.com/source.mp4",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_sonilo_v1_1_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        SoniloV11VideoToSoundEffectsConfig.model_validate(payload)
