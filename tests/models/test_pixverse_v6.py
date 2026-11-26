from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    FalConfig,
    config_class_for_app_id,
    validate_job_schema,
    validate_parameters,
)

TEXT = "fal-ai/pixverse/v6/text-to-video"
IMAGE = "fal-ai/pixverse/v6/image-to-video"
EXTEND = "fal-ai/pixverse/v6/extend"
TRANSITION = "fal-ai/pixverse/v6/transition"
INPUTS = {
    TEXT: {"prompt": "A river flows."},
    IMAGE: {"prompt": "Animate the scene.", "image_url": "https://example.com/start.png"},
    EXTEND: {"prompt": "Continue the scene.", "video_url": "https://example.com/input.mp4"},
    TRANSITION: {
        "prompt": "Transition to night.",
        "first_image_url": "https://example.com/start.png",
        "end_image_url": "https://example.com/end.png",
    },
}


@pytest.fixture(params=INPUTS)
def payload(request: pytest.FixtureRequest) -> dict[str, object]:
    return {"app_id": request.param, **INPUTS[request.param]}


def config_for(payload: dict[str, object]) -> BaseFalConfig:
    config_class = config_class_for_app_id(str(payload["app_id"]))
    assert config_class is not None
    return config_class.model_validate(payload)


def test_pixverse_v6_defaults_match_each_generation_mode(payload: dict[str, object]) -> None:
    expected = {
        **payload,
        "resolution": "720p",
        "duration": 5,
        "negative_prompt": "",
        "style": None,
        "seed": None,
        "generate_audio_switch": False,
    }
    if payload["app_id"] != EXTEND:
        expected.update(
            generate_multi_clip_switch=False, thinking_type=None, enable_safety_checker=True
        )
    if payload["app_id"] in (TEXT, TRANSITION):
        expected["aspect_ratio"] = "16:9"
    assert config_for(payload).model_dump() == expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 1),
        ("duration", 15),
        ("resolution", "360p"),
        ("resolution", "540p"),
        ("resolution", "720p"),
        ("resolution", "1080p"),
        ("style", "anime"),
        ("style", "3d_animation"),
        ("style", "clay"),
        ("style", "comic"),
        ("style", "cyberpunk"),
    ],
)
def test_pixverse_v6_accepts_duration_boundaries_resolutions_and_styles(
    payload: dict[str, object], field: str, value: object
) -> None:
    assert getattr(config_for({**payload, field: value}), field) == value


@pytest.mark.parametrize(
    ("field", "value"),
    [("duration", 0), ("duration", 16), ("resolution", "4K"), ("style", "realistic")],
)
def test_pixverse_v6_rejects_invalid_generation_options(
    payload: dict[str, object], field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({**payload, field: value})


@pytest.mark.parametrize("field", ["prompt", "negative_prompt"])
def test_pixverse_v6_checks_utf8_bytes_for_both_prompts(
    payload: dict[str, object], field: str
) -> None:
    text = "あ" * 682 + "ab"
    assert getattr(config_for({**payload, field: text}), field) == text
    with pytest.raises(ValidationError, match=field):
        config_for({**payload, field: "あ" * 683})


def test_pixverse_v6_accepts_seed_and_audio_options(payload: dict[str, object]) -> None:
    config = config_for({**payload, "seed": -1, "generate_audio_switch": True})
    assert config.seed == -1
    assert config.generate_audio_switch is True


@pytest.mark.parametrize(
    ("app_id", "field"),
    [(app_id, field) for app_id, parameters in INPUTS.items() for field in parameters],
)
def test_pixverse_v6_requires_each_mode_input(app_id: str, field: str) -> None:
    parameters = {key: value for key, value in INPUTS[app_id].items() if key != field}
    with pytest.raises(ValidationError, match=field):
        config_for({"app_id": app_id, **parameters})


@pytest.mark.parametrize(
    "aspect_ratio", ["16:9", "4:3", "1:1", "3:4", "9:16", "2:3", "3:2", "21:9"]
)
def test_pixverse_v6_transition_accepts_aspect_ratios(aspect_ratio: str) -> None:
    config = config_for({"app_id": TRANSITION, **INPUTS[TRANSITION], "aspect_ratio": aspect_ratio})
    assert config.aspect_ratio == aspect_ratio


def test_pixverse_v6_transition_rejects_unsupported_aspect_ratio() -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_for({"app_id": TRANSITION, **INPUTS[TRANSITION], "aspect_ratio": "auto"})


@pytest.mark.parametrize("thinking_type", [None, "enabled", "disabled", "auto"])
def test_pixverse_v6_transition_accepts_prompt_optimization(thinking_type: str | None) -> None:
    config = config_for(
        {
            "app_id": TRANSITION,
            **INPUTS[TRANSITION],
            "thinking_type": thinking_type,
            "generate_multi_clip_switch": True,
            "enable_safety_checker": False,
        }
    )
    assert config.thinking_type == thinking_type
    assert config.generate_multi_clip_switch is True
    assert config.enable_safety_checker is False


@pytest.mark.parametrize(
    "field",
    ["aspect_ratio", "generate_multi_clip_switch", "thinking_type", "enable_safety_checker"],
)
def test_pixverse_v6_extend_rejects_options_not_supported_by_extension(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({"app_id": EXTEND, **INPUTS[EXTEND], field: None})


def test_pixverse_v6_endpoints_are_registered_with_seed_metadata(
    payload: dict[str, object],
) -> None:
    app_id = str(payload["app_id"])
    assert app_id in SUPPORTED_APP_IDS
    config = config_for(payload)
    assert config.random_seed_field == "seed"
    assert isinstance(TypeAdapter(FalConfig).validate_python(payload), type(config))
    assert isinstance(validate_parameters(app_id, INPUTS[app_id]), type(config))


def test_models_lists_all_pixverse_v6_endpoints() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert INPUTS.keys() <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", INPUTS)
def test_schema_prints_valid_job_yaml_for_pixverse_v6_endpoints(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    job = validate_job_schema(YAML(typ="safe").load(result.stdout))
    assert job.app_id == app_id
    assert INPUTS[app_id].keys() <= job.parameters.keys()
    config = config_for({"app_id": app_id, **job.parameters})
    assert config.model_dump(exclude={"app_id"}) == job.parameters
