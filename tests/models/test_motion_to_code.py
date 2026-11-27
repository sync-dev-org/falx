from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_IDS = ("fal-ai/motion-to-code/glsl", "fal-ai/motion-to-code/gsap")
VIDEO_URL = "https://example.com/reference.mp4"
IMAGE_URL = "https://example.com/reference.png"


@pytest.mark.parametrize("app_id", APP_IDS)
def test_motion_to_code_registers_and_preserves_input_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, {"prompt": "A ball bounces."})
    assert config is not None
    assert type(config) is config_class_for_app_id(app_id)
    assert TypeAdapter(FalConfig).validate_python(config.model_dump()) == config
    assert config.random_seed_field is None
    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "A ball bounces.",
        "video_url": None,
        "image_url": None,
        "audio_url": None,
        "duration": 6,
        "aspect_ratio": "16:9",
        "refine_rounds": 1,
        "enable_safety_checker": True,
    }


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("reference", [{"video_url": VIDEO_URL}, {"image_url": IMAGE_URL}])
def test_motion_to_code_accepts_a_reference_without_a_prompt(
    app_id: str, reference: dict[str, str]
) -> None:
    config = validate_parameters(app_id, reference)
    assert config is not None
    assert config.prompt == ""
    assert all(config.model_dump()[key] == value for key, value in reference.items())


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"prompt": "", "image_url": None, "video_url": None},
        {"audio_url": "https://example.com/audio.mp3"},
        {"image_url": IMAGE_URL, "video_url": VIDEO_URL},
        {"prompt": "Animate this.", "image_url": IMAGE_URL, "video_url": VIDEO_URL},
    ],
)
def test_motion_to_code_requires_an_input_and_rejects_conflicting_references(
    app_id: str, parameters: dict[str, object]
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x" * 4000),
        ("duration", 1),
        ("duration", 15),
        ("duration", 2.5),
        ("aspect_ratio", "16:9"),
        ("aspect_ratio", "9:16"),
        ("aspect_ratio", "1:1"),
        ("refine_rounds", 0),
        ("refine_rounds", 1),
        ("audio_url", "https://example.com/audio.mp3"),
        ("audio_url", None),
        ("enable_safety_checker", False),
    ],
)
def test_motion_to_code_accepts_input_limits_and_options(
    app_id: str, field: str, value: object
) -> None:
    config = validate_parameters(app_id, {"prompt": "A loop.", field: value})
    assert config is not None
    assert config.model_dump()[field] == value


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x" * 4001),
        ("prompt", None),
        ("duration", 0.99),
        ("duration", 15.01),
        ("duration", None),
        ("aspect_ratio", "4:3"),
        ("refine_rounds", -1),
        ("refine_rounds", 2),
        ("refine_rounds", 0.5),
        ("enable_safety_checker", None),
        ("seed", 42),
        ("unexpected", True),
    ],
)
def test_motion_to_code_rejects_values_outside_input_constraints(
    app_id: str, field: str, value: object
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {"prompt": "A loop.", field: value})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_motion_to_code_exposes_input_bounds_and_nullable_defaults(app_id: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    schema = config_class.model_json_schema()
    properties = schema["properties"]
    assert schema["required"] == ["app_id"]
    assert properties["prompt"]["maxLength"] == 4000
    assert properties["prompt"]["default"] == ""
    assert properties["duration"]["minimum"] == 1
    assert properties["duration"]["maximum"] == 15
    assert properties["refine_rounds"]["minimum"] == 0
    assert properties["refine_rounds"]["maximum"] == 1
    for field in ("video_url", "image_url", "audio_url"):
        assert properties[field]["anyOf"] == [{"type": "string"}, {"type": "null"}]
        assert properties[field]["default"] is None
