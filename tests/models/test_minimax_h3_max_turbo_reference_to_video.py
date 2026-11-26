from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx import models
from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_ID = "minimax/h3-max-turbo/reference-to-video"
PARAMETERS = {"prompt": "Use Image 1, Video 1, and Audio 1.", "prompt_expansion_mode": "balanced"}


@pytest.fixture
def config_class() -> type[BaseFalConfig]:
    config = config_class_for_app_id(APP_ID)
    assert config is not None
    assert models.MinimaxH3MaxTurboReferenceToVideoConfig is config
    return config


def test_minimax_h3_max_turbo_reference_to_video_accepts_schema_defaults(
    config_class: type[BaseFalConfig],
) -> None:
    config = config_class.model_validate({"app_id": APP_ID, **PARAMETERS})
    assert config.model_dump() == {
        "app_id": APP_ID,
        **PARAMETERS,
        "duration": 5,
        "resolution": "768P",
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "aspect_ratio": "adaptive",
        "reference_image_urls": [],
        "reference_video_urls": [],
        "reference_audio_urls": [],
        "target_audio_url": None,
        "reference_conditions": [],
    }


def test_minimax_h3_max_turbo_reference_to_video_accepts_all_fields(
    config_class: type[BaseFalConfig],
) -> None:
    payload = {
        "app_id": APP_ID,
        "prompt": PARAMETERS["prompt"],
        "prompt_expansion_mode": "quality",
        "duration": 2.5,
        "resolution": "1080P",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
        "aspect_ratio": "9:16",
        "reference_image_urls": ["https://example.com/subject.png"],
        "reference_video_urls": ["https://example.com/motion.mp4"],
        "reference_audio_urls": [],
        "target_audio_url": "https://example.com/soundtrack.wav",
        "reference_conditions": [],
    }
    assert config_class.model_validate(payload).model_dump() == payload


def test_minimax_h3_max_turbo_reference_to_video_preserves_required_schema_default(
    config_class: type[BaseFalConfig],
) -> None:
    schema = config_class.model_json_schema()
    assert set(schema["required"]) == {"app_id", "prompt", "prompt_expansion_mode"}
    assert schema["properties"]["prompt_expansion_mode"]["default"] == "balanced"


@pytest.mark.parametrize("duration", [0.92, 1.5, 15])
def test_minimax_h3_max_turbo_reference_to_video_accepts_fractional_duration(
    config_class: type[BaseFalConfig], duration: float
) -> None:
    config = config_class.model_validate({"app_id": APP_ID, **PARAMETERS, "duration": duration})
    assert config.model_dump()["duration"] == duration


@pytest.mark.parametrize("resolution", ["480P", "768P", "1080P"])
def test_minimax_h3_max_turbo_reference_to_video_accepts_resolution_enum(
    config_class: type[BaseFalConfig], resolution: str
) -> None:
    config = config_class.model_validate({"app_id": APP_ID, **PARAMETERS, "resolution": resolution})
    assert config.model_dump()["resolution"] == resolution


@pytest.mark.parametrize("aspect_ratio", ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_minimax_h3_max_turbo_reference_to_video_accepts_aspect_ratio_enum(
    config_class: type[BaseFalConfig], aspect_ratio: str
) -> None:
    config = config_class.model_validate(
        {"app_id": APP_ID, **PARAMETERS, "aspect_ratio": aspect_ratio}
    )
    assert config.model_dump()["aspect_ratio"] == aspect_ratio


def test_minimax_h3_max_turbo_reference_to_video_accepts_audio_only_references(
    config_class: type[BaseFalConfig],
) -> None:
    urls = ["https://example.com/reference.wav"]
    config = config_class.model_validate(
        {"app_id": APP_ID, **PARAMETERS, "reference_audio_urls": urls}
    )
    assert config.model_dump()["reference_audio_urls"] == urls


def test_minimax_h3_max_turbo_reference_to_video_preserves_ordered_references(
    config_class: type[BaseFalConfig],
) -> None:
    references = [
        {"type": "audio", "url": "https://example.com/reference.wav"},
        {"type": "image", "url": "https://example.com/subject.png"},
        {"type": "video", "url": "https://example.com/motion.mp4"},
    ]
    config = config_class.model_validate(
        {"app_id": APP_ID, **PARAMETERS, "reference_conditions": references}
    )
    assert config.model_dump()["reference_conditions"] == references
    with pytest.raises(ValidationError, match="reference_conditions"):
        config_class.model_validate(
            {"app_id": APP_ID, **PARAMETERS, "reference_conditions": references * 5}
        )
    config = config_class.model_validate(
        {"app_id": APP_ID, **PARAMETERS, "reference_conditions": references * 4}
    )
    assert config.model_dump()["reference_conditions"] == references * 4


@pytest.mark.parametrize(
    ("reference", "needle"),
    [
        ({"type": "image"}, "url"),
        ({"url": "https://example.com/ref.png"}, "type"),
        ({"type": "text", "url": "https://example.com/ref.txt"}, "type"),
        ({"type": "image", "url": ""}, "url"),
    ],
)
def test_minimax_h3_max_turbo_reference_to_video_checks_ordered_reference_fields(
    config_class: type[BaseFalConfig], reference: dict[str, object], needle: str
) -> None:
    with pytest.raises(ValidationError, match=needle):
        config_class.model_validate(
            {"app_id": APP_ID, **PARAMETERS, "reference_conditions": [reference]}
        )


@pytest.mark.parametrize(
    "field_name", ["reference_image_urls", "reference_video_urls", "reference_audio_urls"]
)
def test_minimax_h3_max_turbo_reference_to_video_rejects_mixed_reference_forms(
    config_class: type[BaseFalConfig], field_name: str
) -> None:
    with pytest.raises(ValidationError, match="reference_conditions"):
        config_class.model_validate(
            {
                "app_id": APP_ID,
                **PARAMETERS,
                "reference_conditions": [{"type": "image", "url": "https://example.com/ref.png"}],
                field_name: ["https://example.com/reference"],
            }
        )


@pytest.mark.parametrize("ordered", [False, True])
def test_minimax_h3_max_turbo_reference_to_video_rejects_reference_and_target_audio(
    config_class: type[BaseFalConfig], ordered: bool
) -> None:
    references = (
        {"reference_conditions": [{"type": "audio", "url": "https://example.com/ref.wav"}]}
        if ordered
        else {"reference_audio_urls": ["https://example.com/ref.wav"]}
    )
    with pytest.raises(ValidationError, match="target_audio_url"):
        config_class.model_validate(
            {
                "app_id": APP_ID,
                **PARAMETERS,
                "target_audio_url": "https://example.com/target.wav",
                **references,
            }
        )


def test_minimax_h3_max_turbo_reference_to_video_requires_two_seconds_with_target_audio(
    config_class: type[BaseFalConfig],
) -> None:
    payload = {
        "app_id": APP_ID,
        **PARAMETERS,
        "target_audio_url": "data:audio/wav;base64,YQ==",
    }
    with pytest.raises(ValidationError, match="duration"):
        config_class.model_validate({**payload, "duration": 1.99})
    config = config_class.model_validate({**payload, "duration": 2})
    assert config.model_dump()["duration"] == 2


@pytest.mark.parametrize(
    ("field_name", "limit"),
    [("reference_image_urls", 9), ("reference_video_urls", 3), ("reference_audio_urls", 3)],
)
def test_minimax_h3_max_turbo_reference_to_video_checks_array_limits(
    config_class: type[BaseFalConfig], field_name: str, limit: int
) -> None:
    urls = [f"https://example.com/ref-{index}" for index in range(limit)]
    config = config_class.model_validate({"app_id": APP_ID, **PARAMETERS, field_name: urls})
    assert config.model_dump()[field_name] == urls
    with pytest.raises(ValidationError, match=field_name):
        config_class.model_validate({"app_id": APP_ID, **PARAMETERS, field_name: urls + urls[:1]})
    with pytest.raises(ValidationError, match=field_name):
        config_class.model_validate({"app_id": APP_ID, **PARAMETERS, field_name: None})


def test_minimax_h3_max_turbo_reference_to_video_limits_total_files(
    config_class: type[BaseFalConfig],
) -> None:
    payload = {
        "app_id": APP_ID,
        **PARAMETERS,
        "reference_image_urls": [f"https://example.com/{index}.png" for index in range(9)],
        "reference_video_urls": [f"https://example.com/{index}.mp4" for index in range(3)],
    }
    config = config_class.model_validate(payload)
    assert len(config.model_dump()["reference_image_urls"]) == 9
    assert len(config.model_dump()["reference_video_urls"]) == 3
    with pytest.raises(ValidationError, match="12"):
        config_class.model_validate(
            {**payload, "reference_audio_urls": ["https://example.com/ref.wav"]}
        )


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"prompt_expansion_mode": "balanced"}, "prompt"),
        ({"prompt": "A quiet ocean at dusk."}, "prompt_expansion_mode"),
        ({**PARAMETERS, "prompt_expansion_mode": None}, "prompt_expansion_mode"),
        ({**PARAMETERS, "prompt": ""}, "prompt"),
        ({**PARAMETERS, "prompt": "x" * 50_001}, "prompt"),
        ({**PARAMETERS, "duration": 0.91}, "duration"),
        ({**PARAMETERS, "duration": 15.01}, "duration"),
        ({**PARAMETERS, "resolution": "2K"}, "resolution"),
        ({**PARAMETERS, "aspect_ratio": "2:1"}, "aspect_ratio"),
        ({**PARAMETERS, "target_audio_url": ""}, "target_audio_url"),
        ({**PARAMETERS, "target_audio_url": " \t\n"}, "target_audio_url"),
        ({**PARAMETERS, "reference_conditions": None}, "reference_conditions"),
        ({**PARAMETERS, "unexpected": True}, "unexpected"),
    ],
)
def test_minimax_h3_max_turbo_reference_to_video_rejects_invalid_parameters(
    config_class: type[BaseFalConfig], parameters: dict[str, object], needle: str
) -> None:
    with pytest.raises(ValidationError, match=needle):
        config_class.model_validate({"app_id": APP_ID, **parameters})


def test_minimax_h3_max_turbo_reference_to_video_does_not_invent_prompt_expansion_enum(
    config_class: type[BaseFalConfig],
) -> None:
    config = config_class.model_validate(
        {"app_id": APP_ID, **PARAMETERS, "prompt_expansion_mode": "provider-defined-mode"}
    )
    assert config.model_dump()["prompt_expansion_mode"] == "provider-defined-mode"


def test_minimax_h3_max_turbo_reference_to_video_routes_through_registry(
    config_class: type[BaseFalConfig],
) -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    assert isinstance(adapter.validate_python({"app_id": APP_ID, **PARAMETERS}), config_class)
    assert isinstance(validate_parameters(APP_ID, PARAMETERS), config_class)
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class.random_seed_field == "seed"
