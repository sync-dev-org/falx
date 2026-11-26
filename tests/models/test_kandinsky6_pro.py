from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, config_class_for_app_id

APP_IDS = ["fal-ai/kandinsky6-pro/text-to-video", "fal-ai/kandinsky6-pro/image-to-video"]


@pytest.fixture(params=APP_IDS)
def payload(request: pytest.FixtureRequest) -> dict[str, object]:
    result = {"app_id": request.param, "prompt": "A cat plays a piano."}
    if request.param.endswith("/image-to-video"):
        result["image_url"] = "https://example.com/start.png"
    return result


def config_for(payload: dict[str, object]) -> BaseFalConfig:
    config_class = config_class_for_app_id(str(payload["app_id"]))
    assert config_class is not None
    return config_class.model_validate(payload)


def test_kandinsky6_pro_defaults_match_the_generation_mode(payload: dict[str, object]) -> None:
    assert config_for(payload).model_dump() == {
        **payload,
        "negative_prompt": None,
        "aspect_ratio": "auto" if "image_url" in payload else "16:9",
        "generate_audio": True,
        "enable_prompt_expansion": False,
        "upscale_factor": None,
        "seed": None,
        "sync_mode": False,
        "num_inference_steps": 50,
        "guidance_scale": 5,
        "enable_safety_checker": True,
    }


@pytest.mark.parametrize("num_inference_steps", [8, 50])
@pytest.mark.parametrize("guidance_scale", [1, 10])
def test_kandinsky6_pro_accepts_denoising_boundaries(
    payload: dict[str, object], num_inference_steps: int, guidance_scale: float
) -> None:
    config = config_for(
        {**payload, "num_inference_steps": num_inference_steps, "guidance_scale": guidance_scale}
    )
    assert config.num_inference_steps == num_inference_steps
    assert config.guidance_scale == guidance_scale


@pytest.mark.parametrize("upscale_factor", [None, 2, 2.25, 4])
def test_kandinsky6_pro_accepts_documented_upscale_factors(
    payload: dict[str, object], upscale_factor: float | None
) -> None:
    config = config_for({**payload, "upscale_factor": upscale_factor})
    assert config.upscale_factor == upscale_factor


@pytest.mark.parametrize("aspect_ratio", ["16:9", "9:16", "1:1", "4:3", "3:4"])
def test_kandinsky6_pro_accepts_aspect_ratios(
    payload: dict[str, object], aspect_ratio: str
) -> None:
    assert config_for({**payload, "aspect_ratio": aspect_ratio}).aspect_ratio == aspect_ratio


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("num_inference_steps", 7),
        ("num_inference_steps", 51),
        ("guidance_scale", 0.99),
        ("guidance_scale", 10.01),
        ("upscale_factor", 3),
        ("aspect_ratio", "21:9"),
    ],
)
def test_kandinsky6_pro_rejects_invalid_generation_options(
    payload: dict[str, object], field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for({**payload, field: value})


def test_kandinsky6_pro_accepts_audio_prompt_and_output_options(payload: dict[str, object]) -> None:
    supplied = {
        **payload,
        "negative_prompt": "blur",
        "generate_audio": False,
        "enable_prompt_expansion": True,
        "seed": 42,
        "sync_mode": True,
        "enable_safety_checker": False,
    }
    assert config_for(supplied).model_dump().items() >= supplied.items()


def test_kandinsky6_pro_text_rejects_automatic_aspect_ratio() -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_for({"app_id": APP_IDS[0], "prompt": "A cat.", "aspect_ratio": "auto"})


@pytest.mark.parametrize(
    "payload",
    [
        {"app_id": APP_IDS[0]},
        {"app_id": APP_IDS[1], "image_url": "https://example.com/start.png"},
        {"app_id": APP_IDS[1], "prompt": "Animate the image."},
    ],
)
def test_kandinsky6_pro_requires_prompt_and_image_when_applicable(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        config_for(payload)
