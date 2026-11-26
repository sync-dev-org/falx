from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import BaseFalConfig, FalConfig, config_class_for_app_id, validate_parameters

TEXT_APP_IDS = ("fal-ai/veo3", "fal-ai/veo3/fast")
IMAGE_APP_IDS = ("fal-ai/veo3/image-to-video", "fal-ai/veo3/fast/image-to-video")
APP_IDS = (*TEXT_APP_IDS, *IMAGE_APP_IDS)


@pytest.fixture(params=APP_IDS)
def app_id(request: pytest.FixtureRequest) -> str:
    return request.param


def required_parameters(app_id: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": "A quiet city park."}
    if app_id in IMAGE_APP_IDS:
        parameters["image_url"] = "https://example.com/input.png"
    return parameters


def validated_config(app_id: str, **parameters: object) -> BaseFalConfig:
    config = validate_parameters(app_id, {**required_parameters(app_id), **parameters})
    assert config is not None, f"{app_id} must be registered"
    return config


def test_veo3_accepts_schema_defaults(app_id: str) -> None:
    """Each endpoint validates required inputs and applies its published defaults."""
    config = validated_config(app_id)
    is_image = app_id in IMAGE_APP_IDS

    assert config.model_dump() == {
        "app_id": app_id,
        **required_parameters(app_id),
        "aspect_ratio": "auto" if is_image else "16:9",
        "duration": "8s",
        "negative_prompt": None,
        "resolution": "720p",
        "generate_audio": True,
        "seed": None,
        "auto_fix": not is_image,
        "safety_tolerance": "4",
    }


def test_veo3_accepts_all_parameters(app_id: str) -> None:
    """Explicit parameter values survive validation for regular and fast generation."""
    parameters = {
        **required_parameters(app_id),
        "aspect_ratio": "9:16",
        "duration": "6s",
        "negative_prompt": "blur, distortion",
        "resolution": "1080p",
        "generate_audio": False,
        "seed": -1234,
        "auto_fix": app_id in IMAGE_APP_IDS,
        "safety_tolerance": "6",
    }

    config = validate_parameters(app_id, parameters)

    assert config is not None
    assert config.model_dump() == {"app_id": app_id, **parameters}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aspect_ratio", "16:9"),
        ("aspect_ratio", "9:16"),
        ("duration", "4s"),
        ("duration", "6s"),
        ("duration", "8s"),
        ("resolution", "720p"),
        ("resolution", "1080p"),
        *[("safety_tolerance", str(value)) for value in range(1, 7)],
    ],
)
def test_veo3_accepts_enum_values(app_id: str, field: str, value: str) -> None:
    """The published aspect ratios, durations, resolutions and safety levels are accepted."""
    config = validated_config(app_id, **{field: value})

    assert config.model_dump()[field] == value


@pytest.mark.parametrize("app_id", IMAGE_APP_IDS)
def test_veo3_image_to_video_accepts_auto_aspect_ratio(app_id: str) -> None:
    """Image animation accepts an automatic aspect ratio."""
    config = validated_config(app_id, aspect_ratio="auto")

    assert config.model_dump()["aspect_ratio"] == "auto"


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
def test_veo3_text_to_video_rejects_auto_aspect_ratio(app_id: str) -> None:
    """Text generation requires a supported explicit aspect ratio."""
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validated_config(app_id, aspect_ratio="auto")


@pytest.mark.parametrize("prompt", ["", "a" * 20_000], ids=["empty", "maximum"])
def test_veo3_accepts_prompt_boundaries(app_id: str, prompt: str) -> None:
    """The prompt has no minimum length and accepts exactly 20,000 characters."""
    config = validated_config(app_id, prompt=prompt)

    assert config.model_dump()["prompt"] == prompt


def test_veo3_rejects_prompt_over_limit(app_id: str) -> None:
    """Prompts longer than the published 20,000-character limit are rejected."""
    with pytest.raises(ValidationError, match="prompt"):
        validated_config(app_id, prompt="a" * 20_001)


@pytest.mark.parametrize("field", ["negative_prompt", "seed"])
def test_veo3_accepts_null_optional_parameters(app_id: str, field: str) -> None:
    """The optional negative prompt and seed may be explicitly null."""
    config = validated_config(app_id, **{field: None})

    assert config.model_dump()[field] is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aspect_ratio", "1:1"),
        ("duration", "5s"),
        ("resolution", "4k"),
        ("safety_tolerance", "0"),
        ("safety_tolerance", "7"),
        ("generate_audio", None),
        ("auto_fix", None),
        ("seed", 1.5),
        ("negative_prompt", 123),
        ("unexpected", True),
    ],
)
def test_veo3_rejects_invalid_parameters(app_id: str, field: str, value: object) -> None:
    """Invalid enums, non-nullable values, parameter types and unknown fields are rejected."""
    with pytest.raises(ValidationError, match=field):
        validated_config(app_id, **{field: value})


def test_veo3_requires_prompt(app_id: str) -> None:
    """Every generation endpoint rejects a missing prompt."""
    parameters = required_parameters(app_id)
    del parameters["prompt"]

    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", IMAGE_APP_IDS)
def test_veo3_image_to_video_requires_image(app_id: str) -> None:
    """Image animation rejects requests without an input image."""
    with pytest.raises(ValidationError, match="image_url"):
        validate_parameters(app_id, {"prompt": "Animate the subject."})


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
def test_veo3_text_to_video_rejects_image_parameter(app_id: str) -> None:
    """Text generation rejects an image parameter outside its schema."""
    with pytest.raises(ValidationError, match="image_url"):
        validated_config(app_id, image_url="https://example.com/input.png")


def test_veo3_discriminator_routes_to_registered_config(app_id: str) -> None:
    """The app identifier routes jobs to the matching configuration with seed metadata."""
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    adapter: TypeAdapter[object] = TypeAdapter(FalConfig)

    parsed = adapter.validate_python({"app_id": app_id, **required_parameters(app_id)})

    assert type(parsed) is config_class
    assert parsed.model_dump()["app_id"] == app_id
    assert config_class.random_seed_field == "seed"
