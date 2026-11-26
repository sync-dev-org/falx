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
    "minimax/h3/text-to-video/lora": "MinimaxH3TextToVideoLoraConfig",
    "minimax/h3/image-to-video/lora": "MinimaxH3ImageToVideoLoraConfig",
    "minimax/h3/reference-to-video/lora": "MinimaxH3ReferenceToVideoLoraConfig",
}
TEXT_APP_ID = "minimax/h3/text-to-video/lora"
IMAGE_APP_ID = "minimax/h3/image-to-video/lora"
REFERENCE_APP_ID = "minimax/h3/reference-to-video/lora"
PROMPT = "A quiet ocean at dusk."
PARAMETERS = {"prompt": PROMPT, "loras": [{"path": "owner/repo"}]}


@pytest.fixture(params=APP_IDS)
def app_id(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def config_class(app_id: str) -> type[BaseFalConfig]:
    config = config_class_for_app_id(app_id)
    assert config is not None
    assert getattr(models, APP_IDS[app_id]) is config
    return config


def test_minimax_h3_lora_accepts_schema_defaults(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    config = config_class.model_validate({"app_id": app_id, **PARAMETERS})
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
        "loras": [{"path": "owner/repo", "scale": 1, "weight_name": None}],
        "aspect_ratio": "16:9" if app_id == TEXT_APP_ID else "adaptive",
    }
    if app_id == IMAGE_APP_ID:
        expected.update(image_url=None, end_image_url=None)
    elif app_id == REFERENCE_APP_ID:
        expected.update(reference_image_urls=[], reference_video_urls=[], reference_audio_urls=[])
    assert config.model_dump() == expected


def test_minimax_h3_lora_accepts_all_fields(app_id: str, config_class: type[BaseFalConfig]) -> None:
    payload = {
        "app_id": app_id,
        "prompt": PROMPT,
        "duration": 15,
        "resolution": "4K",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
        "prompt_expansion_mode": "quality",
        "target_audio_url": "https://example.com/soundtrack.wav",
        "aspect_ratio": "9:16",
        "loras": [
            {"path": "owner/repo", "scale": 0, "weight_name": "first.safetensors"},
            {"path": "https://example.com/lora.safetensors", "scale": 4, "weight_name": None},
            {"path": "other/adapter", "scale": 0.5, "weight_name": "second.safetensors"},
        ],
    }
    if app_id == IMAGE_APP_ID:
        payload.update(
            image_url="https://example.com/start.png", end_image_url="https://example.com/end.png"
        )
    elif app_id == REFERENCE_APP_ID:
        payload.update(
            reference_image_urls=["https://example.com/subject.png"],
            reference_video_urls=["https://example.com/motion.mp4"],
            reference_audio_urls=[],
        )
    assert config_class.model_validate(payload).model_dump() == payload


def test_minimax_h3_lora_requires_one_to_three_adapters_and_a_path(
    config_class: type[BaseFalConfig],
) -> None:
    schema = config_class.model_json_schema()
    assert set(schema["required"]) == {"app_id", "prompt", "loras"}
    loras = schema["properties"]["loras"]
    assert loras["minItems"] == 1
    assert loras["maxItems"] == 3
    adapter = schema["$defs"][loras["items"]["$ref"].split("/")[-1]]
    assert set(adapter["required"]) == {"path"}
    assert adapter["properties"]["scale"]["default"] == 1
    assert adapter["properties"]["scale"]["minimum"] == 0
    assert adapter["properties"]["scale"]["maximum"] == 4


@pytest.mark.parametrize("resolution", ["480P", "768P", "2K", "4K"])
def test_minimax_h3_lora_accepts_resolution_enum(
    app_id: str, config_class: type[BaseFalConfig], resolution: str
) -> None:
    config = config_class.model_validate({"app_id": app_id, **PARAMETERS, "resolution": resolution})
    assert config.model_dump()["resolution"] == resolution


@pytest.mark.parametrize("aspect_ratio", ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_minimax_h3_lora_accepts_aspect_ratio_enum(
    app_id: str, config_class: type[BaseFalConfig], aspect_ratio: str
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, **PARAMETERS, "aspect_ratio": aspect_ratio}
    )
    assert config.model_dump()["aspect_ratio"] == aspect_ratio


@pytest.mark.parametrize("duration", [5, 15])
def test_minimax_h3_lora_accepts_duration_boundaries(
    app_id: str, config_class: type[BaseFalConfig], duration: int
) -> None:
    config = config_class.model_validate({"app_id": app_id, **PARAMETERS, "duration": duration})
    assert config.model_dump()["duration"] == duration


@pytest.mark.parametrize("mode", [None, "disabled", "fast", "provider-defined-mode"])
def test_minimax_h3_lora_accepts_nullable_prompt_expansion_without_an_enum(
    app_id: str, config_class: type[BaseFalConfig], mode: str | None
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, **PARAMETERS, "prompt_expansion_mode": mode}
    )
    assert config.model_dump()["prompt_expansion_mode"] == mode


def test_minimax_h3_lora_does_not_add_constraints_to_weight_paths(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    config = config_class.model_validate(
        {"app_id": app_id, **PARAMETERS, "loras": [{"path": "", "weight_name": ""}]}
    )
    assert config.model_dump()["loras"] == [{"path": "", "scale": 1, "weight_name": ""}]


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"loras": [{"path": "owner/repo"}]}, "prompt"),
        ({"prompt": PROMPT}, "loras"),
        ({**PARAMETERS, "prompt": ""}, "prompt"),
        ({**PARAMETERS, "prompt": "x" * 50_001}, "prompt"),
        ({**PARAMETERS, "loras": []}, "loras"),
        ({**PARAMETERS, "loras": None}, "loras"),
        ({**PARAMETERS, "loras": [{"path": "owner/repo"}] * 4}, "loras"),
        ({**PARAMETERS, "loras": [{"scale": 1}]}, "path"),
        ({**PARAMETERS, "loras": [{"path": None}]}, "path"),
        ({**PARAMETERS, "loras": [{"path": "owner/repo", "scale": -0.01}]}, "scale"),
        ({**PARAMETERS, "loras": [{"path": "owner/repo", "scale": 4.01}]}, "scale"),
        ({**PARAMETERS, "loras": [{"path": "owner/repo", "weight_name": 1}]}, "weight_name"),
        ({**PARAMETERS, "loras": [{"path": "owner/repo", "unexpected": True}]}, "unexpected"),
        ({**PARAMETERS, "duration": 4}, "duration"),
        ({**PARAMETERS, "duration": 16}, "duration"),
        ({**PARAMETERS, "duration": 5.5}, "duration"),
        ({**PARAMETERS, "resolution": "1080P"}, "resolution"),
        ({**PARAMETERS, "aspect_ratio": "2:1"}, "aspect_ratio"),
        ({**PARAMETERS, "target_audio_url": " \t\n"}, "target_audio_url"),
        ({**PARAMETERS, "unexpected": True}, "unexpected"),
    ],
)
def test_minimax_h3_lora_rejects_invalid_parameters(
    app_id: str,
    config_class: type[BaseFalConfig],
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        config_class.model_validate({"app_id": app_id, **parameters})


@pytest.mark.parametrize("field_name", ["image_url", "end_image_url"])
def test_minimax_h3_image_to_video_lora_accepts_one_keyframe(field_name: str) -> None:
    config = validate_parameters(
        IMAGE_APP_ID, {**PARAMETERS, field_name: "https://example.com/frame.png"}
    )
    assert config is not None
    assert config.model_dump()[field_name] == "https://example.com/frame.png"
    assert config.model_dump()["aspect_ratio"] == "adaptive"


@pytest.mark.parametrize(
    ("field_name", "limit"),
    [("reference_image_urls", 9), ("reference_video_urls", 3), ("reference_audio_urls", 3)],
)
def test_minimax_h3_reference_to_video_lora_checks_array_limits(
    field_name: str, limit: int
) -> None:
    urls = [f"https://example.com/reference-{index}" for index in range(limit)]
    config = validate_parameters(REFERENCE_APP_ID, {**PARAMETERS, field_name: urls})
    assert config is not None
    assert config.model_dump()[field_name] == urls
    with pytest.raises(ValidationError, match=field_name):
        validate_parameters(REFERENCE_APP_ID, {**PARAMETERS, field_name: urls + urls[:1]})
    with pytest.raises(ValidationError, match=field_name):
        validate_parameters(REFERENCE_APP_ID, {**PARAMETERS, field_name: None})


def test_minimax_h3_reference_to_video_lora_limits_total_files() -> None:
    parameters = {
        **PARAMETERS,
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


def test_minimax_h3_reference_to_video_lora_rejects_target_and_reference_audio() -> None:
    with pytest.raises(ValidationError, match="target_audio_url"):
        validate_parameters(
            REFERENCE_APP_ID,
            {
                **PARAMETERS,
                "target_audio_url": "https://example.com/soundtrack.wav",
                "reference_audio_urls": ["https://example.com/reference.wav"],
            },
        )


def test_minimax_h3_lora_routes_through_registry(
    app_id: str, config_class: type[BaseFalConfig]
) -> None:
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)
    assert isinstance(adapter.validate_python({"app_id": app_id, **PARAMETERS}), config_class)
    assert isinstance(validate_parameters(app_id, PARAMETERS), config_class)
    assert app_id in SUPPORTED_APP_IDS
    assert config_class.random_seed_field == "seed"
