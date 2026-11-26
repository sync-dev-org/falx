from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, config_class_for_app_id

APP_IDS = ["pixverse/v6/max/text-to-video", "pixverse/v6/max/image-to-video"]


@pytest.fixture(params=APP_IDS)
def payload(request: pytest.FixtureRequest) -> dict[str, object]:
    result = {"app_id": request.param, "prompt": "A river flows through the city."}
    if request.param.endswith("/image-to-video"):
        result["image_url"] = "https://example.com/start.png"
    return result


def config_for(payload: dict[str, object]) -> BaseFalConfig:
    config_class = config_class_for_app_id(str(payload["app_id"]))
    assert config_class is not None
    return config_class.model_validate(payload)


def test_pixverse_v6_max_defaults_match_the_generation_mode(payload: dict[str, object]) -> None:
    expected = {
        **payload,
        "resolution": "720p",
        "duration": 5,
        "negative_prompt": "",
        "style": None,
        "seed": None,
        "generate_audio_switch": False,
        "generate_multi_clip_switch": False,
        "thinking_type": None,
        "enable_safety_checker": True,
    }
    if "image_url" not in payload:
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
    ],
)
def test_pixverse_v6_max_accepts_duration_boundaries_and_resolutions(
    payload: dict[str, object], field: str, value: object
) -> None:
    config = config_for({**payload, field: value})
    assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("style", None),
        ("style", "anime"),
        ("style", "3d_animation"),
        ("style", "clay"),
        ("style", "comic"),
        ("style", "cyberpunk"),
        ("thinking_type", None),
        ("thinking_type", "enabled"),
        ("thinking_type", "disabled"),
        ("thinking_type", "auto"),
    ],
)
def test_pixverse_v6_max_accepts_styles_and_prompt_optimization(
    payload: dict[str, object], field: str, value: object
) -> None:
    config = config_for({**payload, field: value})
    assert getattr(config, field) == value


@pytest.mark.parametrize("field", ["prompt", "negative_prompt"])
@pytest.mark.parametrize("text", ["x" * 2048, "あ" * 682 + "ab", "😀" * 512])
def test_pixverse_v6_max_accepts_exact_utf8_byte_limit(
    payload: dict[str, object], field: str, text: str
) -> None:
    config = config_for({**payload, field: text})
    assert getattr(config, field) == text


@pytest.mark.parametrize("field", ["prompt", "negative_prompt"])
@pytest.mark.parametrize("text", ["x" * 2049, "あ" * 683, "😀" * 513])
def test_pixverse_v6_max_rejects_prompts_over_utf8_byte_limit(
    payload: dict[str, object], field: str, text: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({**payload, field: text})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 0),
        ("duration", 16),
        ("resolution", "4K"),
        ("style", "realistic"),
        ("thinking_type", "yes"),
    ],
)
def test_pixverse_v6_max_rejects_invalid_generation_options(
    payload: dict[str, object], field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({**payload, field: value})


def test_pixverse_v6_max_accepts_seed_audio_and_safety_options(payload: dict[str, object]) -> None:
    supplied = {
        **payload,
        "seed": 42,
        "generate_audio_switch": True,
        "generate_multi_clip_switch": True,
        "enable_safety_checker": False,
    }
    assert config_for(supplied).model_dump().items() >= supplied.items()


@pytest.mark.parametrize(
    "aspect_ratio", ["16:9", "4:3", "1:1", "3:4", "9:16", "2:3", "3:2", "21:9"]
)
def test_pixverse_v6_max_text_accepts_aspect_ratios(aspect_ratio: str) -> None:
    config = config_for({"app_id": APP_IDS[0], "prompt": "A river.", "aspect_ratio": aspect_ratio})
    assert config.aspect_ratio == aspect_ratio


def test_pixverse_v6_max_text_rejects_unsupported_aspect_ratio() -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_for({"app_id": APP_IDS[0], "prompt": "A river.", "aspect_ratio": "auto"})


@pytest.mark.parametrize(
    "payload",
    [
        {"app_id": APP_IDS[0]},
        {"app_id": APP_IDS[1], "image_url": "https://example.com/start.png"},
        {"app_id": APP_IDS[1], "prompt": "Animate the image."},
    ],
)
def test_pixverse_v6_max_requires_prompt_and_image_when_applicable(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        config_for(payload)


def test_pixverse_v6_max_image_rejects_text_only_aspect_ratio() -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_for(
            {
                "app_id": APP_IDS[1],
                "prompt": "Animate the image.",
                "image_url": "https://example.com/start.png",
                "aspect_ratio": "16:9",
            }
        )
