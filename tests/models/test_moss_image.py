from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import MossImageConfig, MossImageSize

APP_ID = "fal-ai/moss-image"


def test_moss_image_accepts_required_prompt_with_api_defaults() -> None:
    config = MossImageConfig(app_id=APP_ID, prompt="A ceramic bowl on a wooden table.")

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A ceramic bowl on a wooden table.",
        "negative_prompt": "",
        "enable_prompt_expansion": True,
        "image_size": "square_hd",
        "num_inference_steps": 50,
        "guidance_scale": 3,
        "seed": None,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "jpeg",
        "sync_mode": False,
    }


@pytest.mark.parametrize(
    ("num_inference_steps", "guidance_scale", "num_images"),
    [(1, 0, 1), (100, 10, 4)],
)
def test_moss_image_accepts_all_fields_and_numeric_boundaries(
    num_inference_steps: int, guidance_scale: float, num_images: int
) -> None:
    config = MossImageConfig(
        app_id=APP_ID,
        prompt="x" * 16384,
        negative_prompt="y" * 16384,
        enable_prompt_expansion=False,
        image_size={"width": 14142, "height": 1},
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        seed=-1,
        num_images=num_images,
        enable_safety_checker=False,
        output_format="webp",
        sync_mode=True,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "x" * 16384,
        "negative_prompt": "y" * 16384,
        "enable_prompt_expansion": False,
        "image_size": {"width": 14142, "height": 1},
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "seed": -1,
        "num_images": num_images,
        "enable_safety_checker": False,
        "output_format": "webp",
        "sync_mode": True,
    }


@pytest.mark.parametrize(
    "image_size",
    ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
)
def test_moss_image_accepts_size_presets(image_size: str) -> None:
    config = MossImageConfig(app_id=APP_ID, prompt="A forest.", image_size=image_size)

    assert config.image_size == image_size


@pytest.mark.parametrize("output_format", ["jpeg", "png", "webp"])
def test_moss_image_accepts_output_formats(output_format: str) -> None:
    config = MossImageConfig(app_id=APP_ID, prompt="A forest.", output_format=output_format)

    assert config.output_format == output_format


def test_moss_image_preserves_custom_size_defaults_and_schema_constraints() -> None:
    assert MossImageSize().model_dump() == {"width": 512, "height": 512}
    schema = MossImageConfig.model_json_schema()
    assert set(schema["required"]) == {"app_id", "prompt"}
    properties = schema["properties"]
    assert properties["prompt"]["minLength"] == 1
    assert properties["prompt"]["maxLength"] == 16384
    assert properties["negative_prompt"]["maxLength"] == 16384
    assert properties["num_inference_steps"]["minimum"] == 1
    assert properties["num_inference_steps"]["maximum"] == 100
    assert properties["guidance_scale"]["minimum"] == 0
    assert properties["guidance_scale"]["maximum"] == 10
    assert properties["num_images"]["minimum"] == 1
    assert properties["num_images"]["maximum"] == 4
    for dimension in ("width", "height"):
        size_property = schema["$defs"]["MossImageSize"]["properties"][dimension]
        assert size_property["exclusiveMinimum"] == 0
        assert size_property["maximum"] == 14142


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "prompt"),
        ({"prompt": ""}, "prompt"),
        ({"prompt": "x" * 16385}, "prompt"),
        ({"negative_prompt": "x" * 16385}, "negative_prompt"),
        ({"negative_prompt": None}, "negative_prompt"),
        ({"num_inference_steps": 0}, "num_inference_steps"),
        ({"num_inference_steps": 101}, "num_inference_steps"),
        ({"guidance_scale": -0.1}, "guidance_scale"),
        ({"guidance_scale": 10.1}, "guidance_scale"),
        ({"num_images": 0}, "num_images"),
        ({"num_images": 5}, "num_images"),
        ({"image_size": "auto"}, "image_size"),
        ({"image_size": None}, "image_size"),
        ({"image_size": {"width": 0}}, "width"),
        ({"image_size": {"height": 14143}}, "height"),
        ({"output_format": "gif"}, "output_format"),
        ({"seed": "random"}, "seed"),
        ({"sync_mode": None}, "sync_mode"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_moss_image_rejects_invalid_parameters(parameters: dict[str, object], needle: str) -> None:
    payload = {"app_id": APP_ID, "prompt": "A forest.", **parameters}
    if not parameters:
        payload.pop("prompt")
    with pytest.raises(ValidationError, match=needle):
        MossImageConfig.model_validate(payload)
