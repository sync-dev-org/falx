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

APP_IDS = {
    "minimax/h3/text-to-video": "MinimaxH3TextToVideoConfig",
    "minimax/h3/image-to-video": "MinimaxH3ImageToVideoConfig",
    "minimax/h3/reference-to-video": "MinimaxH3ReferenceToVideoConfig",
}
TEXT_APP_ID = "minimax/h3/text-to-video"
IMAGE_APP_ID = "minimax/h3/image-to-video"
REFERENCE_APP_ID = "minimax/h3/reference-to-video"
PROMPT = "A quiet ocean at dusk."


@pytest.fixture(params=APP_IDS)
def app_id(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def config_class(app_id: str) -> type[BaseFalConfig]:
    config = config_class_for_app_id(app_id)
    assert config is not None
    assert getattr(models, APP_IDS[app_id]) is config
    return config


def test_minimax_h3_accepts_schema_defaults(app_id: str, config_class: type[BaseFalConfig]) -> None:
    config = config_class.model_validate({"app_id": app_id, "prompt": PROMPT})
    expected = {
        "app_id": app_id,
        "prompt": PROMPT,
        "duration": 5,
        "resolution": "2K",
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
        "prompt_expansion_mode": "balanced",
        "target_audio_url": None,
    }
    if app_id == TEXT_APP_ID:
        expected["aspect_ratio"] = "16:9"
    elif app_id == IMAGE_APP_ID:
        expected.update(image_url=None, end_image_url=None)
    else:
        expected.update(
            aspect_ratio="adaptive",
            reference_image_urls=[],
            reference_video_urls=[],
            reference_audio_urls=[],
        )
    assert config.model_dump() == expected


def test_minimax_h3_accepts_all_fields(app_id: str, config_class: type[BaseFalConfig]) -> None:
    payload = {
        "app_id": app_id,
        "prompt": "Use Image 1 and Video 1 to guide the scene.",
        "duration": 15,
        "resolution": "4K",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
        "prompt_expansion_mode": "quality",
        "target_audio_url": "data:audio/wav;base64,YQ==",
    }
    if app_id == TEXT_APP_ID:
        payload["aspect_ratio"] = "9:16"
    elif app_id == IMAGE_APP_ID:
        payload.update(
            image_url="https://example.com/start.png",
            end_image_url="https://example.com/end.png",
        )
    else:
        payload.update(
            aspect_ratio="21:9",
            reference_image_urls=["https://example.com/subject.png"],
            reference_video_urls=["https://example.com/motion.mp4"],
            reference_audio_urls=[],
        )
    assert config_class.model_validate(payload).model_dump() == payload


def test_minimax_h3_schema_has_only_prompt_and_app_id_required(
    config_class: type[BaseFalConfig],
) -> None:
    schema = config_class.model_json_schema()
    assert set(schema["required"]) == {"app_id", "prompt"}
    assert schema["properties"]["prompt_expansion_mode"]["default"] == "balanced"


@pytest.mark.parametrize("mode", [None, "disabled", "fast", "provider-defined-mode"])
def test_minimax_h3_accepts_nullable_and_unrestricted_prompt_expansion(
    app_id: str, config_class: type[BaseFalConfig], mode: str | None
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, "prompt": PROMPT, "prompt_expansion_mode": mode}
    )
    assert config.model_dump()["prompt_expansion_mode"] == mode


@pytest.mark.parametrize("resolution", ["480P", "768P", "2K", "4K"])
def test_minimax_h3_accepts_resolution_enum(
    app_id: str, config_class: type[BaseFalConfig], resolution: str
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, "prompt": PROMPT, "resolution": resolution}
    )
    assert config.model_dump()["resolution"] == resolution


@pytest.mark.parametrize("duration", [5, 15])
def test_minimax_h3_accepts_duration_boundaries(
    app_id: str, config_class: type[BaseFalConfig], duration: int
) -> None:
    config = config_class.model_validate({"app_id": app_id, "prompt": PROMPT, "duration": duration})
    assert config.model_dump()["duration"] == duration


def test_minimax_h3_accepts_maximum_prompt_length(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    config = config_class.model_validate({"app_id": app_id, "prompt": "x" * 50_000})
    assert len(config.model_dump()["prompt"]) == 50_000


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": ""}, "prompt"),
        ({"prompt": "x" * 50_001}, "prompt"),
        ({"duration": 4}, "duration"),
        ({"duration": 16}, "duration"),
        ({"duration": 5.5}, "duration"),
        ({"resolution": "1080P"}, "resolution"),
        ({"target_audio_url": ""}, "target_audio_url"),
        ({"target_audio_url": " \t\n"}, "target_audio_url"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_minimax_h3_rejects_invalid_parameters(
    app_id: str,
    config_class: type[BaseFalConfig],
    parameters: dict[str, object],
    needle: str,
) -> None:
    payload = {"app_id": app_id, "prompt": PROMPT, **parameters}
    if not parameters:
        payload.pop("prompt")
    with pytest.raises(ValidationError, match=needle):
        config_class.model_validate(payload)


@pytest.mark.parametrize("app_id", [TEXT_APP_ID, REFERENCE_APP_ID])
@pytest.mark.parametrize("aspect_ratio", ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_minimax_h3_accepts_aspect_ratio_enum(app_id: str, aspect_ratio: str) -> None:
    config = validate_parameters(app_id, {"prompt": PROMPT, "aspect_ratio": aspect_ratio})
    assert config is not None
    assert config.model_dump()["aspect_ratio"] == aspect_ratio


@pytest.mark.parametrize("app_id", [TEXT_APP_ID, REFERENCE_APP_ID])
def test_minimax_h3_rejects_invalid_aspect_ratio(app_id: str) -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validate_parameters(app_id, {"prompt": PROMPT, "aspect_ratio": "2:1"})


@pytest.mark.parametrize("app_id", [TEXT_APP_ID, IMAGE_APP_ID])
def test_minimax_h3_does_not_accept_reference_only_fields(app_id: str) -> None:
    with pytest.raises(ValidationError, match="reference_audio_urls"):
        validate_parameters(app_id, {"prompt": PROMPT, "reference_audio_urls": []})


@pytest.mark.parametrize("field_name", ["image_url", "end_image_url"])
def test_minimax_h3_image_to_video_accepts_one_keyframe(field_name: str) -> None:
    config = validate_parameters(
        IMAGE_APP_ID, {"prompt": PROMPT, field_name: "https://example.com/frame.png"}
    )
    assert config is not None
    assert config.model_dump()[field_name] == "https://example.com/frame.png"


def test_minimax_h3_image_to_video_has_no_aspect_ratio_field() -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validate_parameters(IMAGE_APP_ID, {"prompt": PROMPT, "aspect_ratio": "16:9"})


@pytest.mark.parametrize(
    ("field_name", "limit"),
    [("reference_image_urls", 9), ("reference_video_urls", 3), ("reference_audio_urls", 3)],
)
def test_minimax_h3_reference_to_video_checks_array_limits(field_name: str, limit: int) -> None:
    urls = [f"https://example.com/reference-{index}" for index in range(limit)]
    config = validate_parameters(REFERENCE_APP_ID, {"prompt": PROMPT, field_name: urls})
    assert config is not None
    assert config.model_dump()[field_name] == urls
    with pytest.raises(ValidationError, match=field_name):
        validate_parameters(REFERENCE_APP_ID, {"prompt": PROMPT, field_name: urls + urls[:1]})
    with pytest.raises(ValidationError, match=field_name):
        validate_parameters(REFERENCE_APP_ID, {"prompt": PROMPT, field_name: None})


def test_minimax_h3_reference_to_video_accepts_twelve_files_and_rejects_thirteen() -> None:
    parameters = {
        "prompt": PROMPT,
        "reference_image_urls": [f"https://example.com/{index}.png" for index in range(9)],
        "reference_video_urls": [f"https://example.com/{index}.mp4" for index in range(3)],
    }
    config = validate_parameters(REFERENCE_APP_ID, parameters)
    assert config is not None
    assert len(config.model_dump()["reference_image_urls"]) == 9
    assert len(config.model_dump()["reference_video_urls"]) == 3
    with pytest.raises(ValidationError, match="12"):
        validate_parameters(
            REFERENCE_APP_ID,
            {**parameters, "reference_audio_urls": ["https://example.com/audio.wav"]},
        )


def test_minimax_h3_reference_to_video_rejects_target_audio_with_reference_audio() -> None:
    with pytest.raises(ValidationError, match="target_audio_url"):
        validate_parameters(
            REFERENCE_APP_ID,
            {
                "prompt": PROMPT,
                "target_audio_url": "https://example.com/soundtrack.wav",
                "reference_audio_urls": ["https://example.com/reference.wav"],
            },
        )


def test_minimax_h3_routes_through_registry(app_id: str, config_class: type[BaseFalConfig]) -> None:
    payload = {"app_id": app_id, "prompt": PROMPT}
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    assert isinstance(adapter.validate_python(payload), config_class)
    assert isinstance(validate_parameters(app_id, {"prompt": PROMPT}), config_class)
    assert app_id in SUPPORTED_APP_IDS
    assert config_class.random_seed_field == "seed"
