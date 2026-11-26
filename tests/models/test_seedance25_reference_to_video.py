from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    Seedance25ReferenceToVideoConfig,
    validate_parameters,
)

APP_ID = "bytedance/seedance-2.5/reference-to-video"
DOCUMENTED_DURATIONS = ["auto", *(str(value) for value in range(4, 31))]
runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_seedance25_reference_to_video_accepts_documented_defaults() -> None:
    config = Seedance25ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Create a continuous shot from the supplied references.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Create a continuous shot from the supplied references.",
        "image_urls": [],
        "video_urls": [],
        "audio_urls": [],
        "resolution": "720p",
        "duration": "auto",
        "aspect_ratio": "auto",
        "generate_audio": True,
        "bitrate_mode": "standard",
        "end_user_id": None,
    }


def test_seedance25_reference_to_video_accepts_all_documented_fields() -> None:
    config = Seedance25ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use @Image1, @Video1, and @Audio1 to guide the shot.",
        image_urls=["https://example.com/hero.png"],
        video_urls=["https://example.com/motion.mp4"],
        audio_urls=["https://example.com/dialogue.wav"],
        resolution="1080p",
        duration="30",
        aspect_ratio="16:9",
        generate_audio=False,
        bitrate_mode="high",
        end_user_id="user-123",
    )

    assert config.image_urls == ["https://example.com/hero.png"]
    assert config.video_urls == ["https://example.com/motion.mp4"]
    assert config.audio_urls == ["https://example.com/dialogue.wav"]
    assert config.duration == "30"
    assert config.bitrate_mode == "high"


@pytest.mark.parametrize("field", ["image_urls", "video_urls", "audio_urls"])
def test_seedance25_reference_to_video_rejects_explicit_null_reference_lists(
    field: str,
) -> None:
    payload: dict[str, object] = {
        "app_id": APP_ID,
        "prompt": "Create a continuous shot from the supplied references.",
        field: None,
    }

    with pytest.raises(ValidationError, match=field):
        Seedance25ReferenceToVideoConfig.model_validate(payload)


def test_seedance25_reference_to_video_schema_uses_optional_non_nullable_arrays() -> None:
    schema = Seedance25ReferenceToVideoConfig.model_json_schema()

    for field in ("image_urls", "video_urls", "audio_urls"):
        field_schema = schema["properties"][field]
        assert field not in schema["required"]
        assert field_schema["type"] == "array"
        assert "anyOf" not in field_schema
        assert "default" not in field_schema


def test_seedance25_reference_to_video_schema_example_uses_empty_reference_lists() -> None:
    result = runner.invoke(app, ["schema", APP_ID])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["image_urls"] == []
    assert payload["parameters"]["video_urls"] == []
    assert payload["parameters"]["audio_urls"] == []


@pytest.mark.parametrize("duration", DOCUMENTED_DURATIONS)
def test_seedance25_reference_to_video_accepts_duration_string_enum(duration: str) -> None:
    config = Seedance25ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use @Image1 as the visual reference.",
        image_urls=["https://example.com/hero.png"],
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 4),
        ("duration", "3"),
        ("duration", "31"),
        ("aspect_ratio", "2:1"),
        ("bitrate_mode", "lossless"),
        ("resolution", "4k"),
    ],
)
def test_seedance25_reference_to_video_rejects_undocumented_enum_values(
    field: str,
    value: object,
) -> None:
    payload: dict[str, object] = {
        "app_id": APP_ID,
        "prompt": "Create a continuous shot from the supplied references.",
        field: value,
    }

    with pytest.raises(ValidationError, match=field):
        Seedance25ReferenceToVideoConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "count", "needle"),
    [
        ("image_urls", 31, "image_urls"),
        ("video_urls", 11, "video_urls"),
        ("audio_urls", 11, "audio_urls"),
    ],
)
def test_seedance25_reference_to_video_rejects_too_many_files_per_modality(
    field: str,
    count: int,
    needle: str,
) -> None:
    payload: dict[str, object] = {
        "app_id": APP_ID,
        "prompt": "Create a continuous shot from the supplied references.",
        "image_urls": ["https://example.com/visual.png"],
        field: [f"https://example.com/reference-{index}" for index in range(count)],
    }

    with pytest.raises(ValidationError, match=needle):
        Seedance25ReferenceToVideoConfig.model_validate(payload)


def test_seedance25_reference_to_video_accepts_full_fifty_file_budget() -> None:
    config = Seedance25ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Use the full multimodal reference budget.",
        image_urls=[f"https://example.com/image-{index}.png" for index in range(30)],
        video_urls=[f"https://example.com/video-{index}.mp4" for index in range(10)],
        audio_urls=[f"https://example.com/audio-{index}.wav" for index in range(10)],
    )

    reference_lists = (config.image_urls, config.video_urls, config.audio_urls)
    assert sum(len(urls or []) for urls in reference_lists) == 50


def test_seedance25_reference_to_video_rejects_audio_without_visual_reference() -> None:
    with pytest.raises(ValidationError, match="audio_urls require image_urls or video_urls"):
        Seedance25ReferenceToVideoConfig(
            app_id=APP_ID,
            prompt="Use @Audio1 to guide the shot.",
            audio_urls=["https://example.com/dialogue.wav"],
        )


def test_seedance25_reference_to_video_describes_media_constraints() -> None:
    image_description = Seedance25ReferenceToVideoConfig.model_fields["image_urls"].description
    video_description = Seedance25ReferenceToVideoConfig.model_fields["video_urls"].description
    audio_description = Seedance25ReferenceToVideoConfig.model_fields["audio_urls"].description

    assert image_description is not None
    assert "JPG, PNG, WebP, BMP, TIFF, GIF, HEIC, HEIF" in image_description
    assert "Max 30 MB per image" in image_description
    assert "Total files across all modalities must not exceed 50" in image_description
    assert video_description is not None
    assert "MP4, MOV" in video_description
    assert "1.8 to 30.2 seconds" in video_description
    assert "200 MB" in video_description
    assert "300 to 6,000 pixels per side" in video_description
    assert "24 to 60 FPS" in video_description
    assert audio_description is not None
    assert "MP3, WAV" in audio_description
    assert "15 MB" in audio_description
    assert "combined duration must not exceed 30.2 seconds" in audio_description
    assert "at least one reference image or video is required" in audio_description


def test_seedance25_reference_to_video_is_registered() -> None:
    validated = validate_parameters(
        APP_ID,
        {
            "prompt": "Use @Image1 as the visual reference.",
            "image_urls": ["https://example.com/hero.png"],
        },
    )

    assert APP_ID in SUPPORTED_APP_IDS
    assert isinstance(validated, Seedance25ReferenceToVideoConfig)
