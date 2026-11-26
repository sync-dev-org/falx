from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, config_class_for_app_id

APP_IDS = ["fal-ai/vidu/q4/image-to-video", "fal-ai/vidu/q4/reference-to-video"]


@pytest.fixture(params=APP_IDS)
def payload(request: pytest.FixtureRequest) -> dict[str, object]:
    if request.param.endswith("/image-to-video"):
        return {"app_id": request.param, "image_url": "https://example.com/start.png"}
    return {"app_id": request.param, "prompt": "Animate the references."}


def config_for(payload: dict[str, object]) -> BaseFalConfig:
    config_class = config_class_for_app_id(str(payload["app_id"]))
    assert config_class is not None
    return config_class.model_validate(payload)


def test_vidu_q4_defaults_match_the_generation_mode(payload: dict[str, object]) -> None:
    expected = {
        **payload,
        "duration": 5,
        "seed": None,
        "resolution": "720p",
        "enable_safety_checker": True,
    }
    if "image_url" in payload:
        expected["prompt"] = ""
    else:
        expected.update(
            reference_image_urls=[], reference_audio_urls=[], aspect_ratio="16:9", audio=False
        )
    assert config_for(payload).model_dump() == expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 3),
        ("duration", 16),
        ("resolution", "540p"),
        ("resolution", "720p"),
        ("resolution", "1080p"),
        ("resolution", "2K"),
        ("resolution", "4K"),
    ],
)
def test_vidu_q4_accepts_duration_boundaries_and_resolutions(
    payload: dict[str, object], field: str, value: object
) -> None:
    config = config_for({**payload, field: value})
    assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("field", "value"),
    [("duration", 2), ("duration", 17), ("resolution", "360p"), ("prompt", "x" * 5001)],
)
def test_vidu_q4_rejects_values_outside_documented_limits(
    payload: dict[str, object], field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({**payload, field: value})


def test_vidu_q4_accepts_long_prompt_and_seed_and_safety_options(
    payload: dict[str, object],
) -> None:
    supplied = {**payload, "prompt": "x" * 5000, "seed": -1, "enable_safety_checker": False}
    config = config_for(supplied)
    assert config.model_dump().items() >= supplied.items()


@pytest.mark.parametrize("aspect_ratio", ["16:9", "9:16", "4:3", "3:4", "1:1"])
def test_vidu_q4_reference_accepts_reference_limits_and_audio(aspect_ratio: str) -> None:
    config = config_for(
        {
            "app_id": APP_IDS[1],
            "prompt": "Animate [@reference_image_1] with [reference_audio_1].",
            "reference_image_urls": ["https://example.com/ref.png"] * 12,
            "reference_audio_urls": ["https://example.com/voice.mp3"] * 3,
            "aspect_ratio": aspect_ratio,
            "audio": True,
        }
    )
    assert len(config.reference_image_urls) == 12
    assert len(config.reference_audio_urls) == 3
    assert config.aspect_ratio == aspect_ratio
    assert config.audio is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("reference_image_urls", ["https://example.com/ref.png"] * 13),
        ("reference_audio_urls", ["https://example.com/voice.mp3"] * 4),
        ("prompt", ""),
        ("aspect_ratio", "21:9"),
    ],
)
def test_vidu_q4_reference_rejects_invalid_references_or_prompt(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({"app_id": APP_IDS[1], "prompt": "Animate.", field: value})


@pytest.mark.parametrize(
    ("app_id", "required"), [(APP_IDS[0], "image_url"), (APP_IDS[1], "prompt")]
)
def test_vidu_q4_requires_input_for_the_generation_mode(app_id: str, required: str) -> None:
    with pytest.raises(ValidationError, match=required):
        config_for({"app_id": app_id})


@pytest.mark.parametrize("field", ["end_image_url", "audio", "aspect_ratio"])
def test_vidu_q4_image_rejects_fields_from_other_generation_modes(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({"app_id": APP_IDS[0], "image_url": "data:image/png;base64,AA==", field: None})
