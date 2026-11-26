from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import IdeogramV4Config, IdeogramV4ImageSize

APP_ID = "ideogram/v4"


def test_ideogram_v4_accepts_minimal_required_fields() -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="A red panda perched on a mossy branch at sunrise.",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A red panda perched on a mossy branch at sunrise.",
        "expansion_model": "Medium",
        "image_size": "square_hd",
        "rendering_speed": "BALANCED",
        "acceleration": "none",
        "num_images": 1,
        "seed": None,
        "sync_mode": False,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }


def test_ideogram_v4_accepts_all_fields() -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="Editorial packaging with crisp geometric typography.",
        expansion_model="Large",
        image_size={"width": 1920, "height": 1080},
        rendering_speed="QUALITY",
        acceleration="high",
        num_images=4,
        seed=42,
        sync_mode=True,
        enable_safety_checker=False,
        output_format="png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Editorial packaging with crisp geometric typography.",
        "expansion_model": "Large",
        "image_size": {"width": 1920, "height": 1080},
        "rendering_speed": "QUALITY",
        "acceleration": "high",
        "num_images": 4,
        "seed": 42,
        "sync_mode": True,
        "enable_safety_checker": False,
        "output_format": "png",
    }


def test_ideogram_v4_preserves_required_fields_and_defaults_in_json_schema() -> None:
    schema = IdeogramV4Config.model_json_schema()

    assert set(schema["required"]) == {"app_id", "prompt"}
    assert schema["properties"]["expansion_model"]["default"] == "Medium"
    assert schema["properties"]["image_size"]["default"] == "square_hd"
    assert schema["properties"]["rendering_speed"]["default"] == "BALANCED"
    assert schema["properties"]["acceleration"]["default"] == "none"
    assert schema["properties"]["num_images"]["default"] == 1
    assert schema["properties"]["seed"]["default"] is None
    assert schema["properties"]["sync_mode"]["default"] is False
    assert schema["properties"]["enable_safety_checker"]["default"] is True
    assert schema["properties"]["output_format"]["default"] == "jpeg"


@pytest.mark.parametrize(
    "image_size",
    [
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
    ],
)
def test_ideogram_v4_accepts_image_size_presets(image_size: str) -> None:
    config = IdeogramV4Config(app_id=APP_ID, prompt="A still life.", image_size=image_size)

    assert config.image_size == image_size


def test_ideogram_v4_accepts_custom_image_size_defaults_and_boundaries() -> None:
    default_size = IdeogramV4ImageSize()
    maximum_size = IdeogramV4ImageSize(width=14142, height=14142)
    partial_size = IdeogramV4ImageSize(width=1024)

    assert default_size.model_dump() == {"width": 512, "height": 512}
    assert maximum_size.model_dump() == {"width": 14142, "height": 14142}
    assert partial_size.model_dump() == {"width": 1024, "height": 512}


@pytest.mark.parametrize("expansion_model", ["None", "Medium", "Large"])
def test_ideogram_v4_accepts_expansion_model_enum(expansion_model: str) -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="A still life.",
        expansion_model=expansion_model,
    )

    assert config.expansion_model == expansion_model


@pytest.mark.parametrize("rendering_speed", ["TURBO", "BALANCED", "QUALITY"])
def test_ideogram_v4_accepts_rendering_speed_enum(rendering_speed: str) -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="A still life.",
        rendering_speed=rendering_speed,
    )

    assert config.rendering_speed == rendering_speed


@pytest.mark.parametrize("acceleration", ["none", "low", "regular", "high"])
def test_ideogram_v4_accepts_acceleration_enum(acceleration: str) -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="A still life.",
        acceleration=acceleration,
    )

    assert config.acceleration == acceleration


@pytest.mark.parametrize("output_format", ["jpeg", "png"])
def test_ideogram_v4_accepts_output_format_enum(output_format: str) -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="A still life.",
        output_format=output_format,
    )

    assert config.output_format == output_format


@pytest.mark.parametrize("num_images", [1, 4])
def test_ideogram_v4_accepts_num_images_boundaries(num_images: int) -> None:
    config = IdeogramV4Config(
        app_id=APP_ID,
        prompt="A still life.",
        num_images=num_images,
    )

    assert config.num_images == num_images


def test_ideogram_v4_accepts_empty_prompt_and_nullable_seed() -> None:
    config = IdeogramV4Config(app_id=APP_ID, prompt="", seed=None)

    assert config.prompt == ""
    assert config.seed is None


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "prompt"),
        ({"app_id": APP_ID, "prompt": "x", "expansion_model": "Small"}, "expansion_model"),
        ({"app_id": APP_ID, "prompt": "x", "rendering_speed": "FAST"}, "rendering_speed"),
        ({"app_id": APP_ID, "prompt": "x", "acceleration": "maximum"}, "acceleration"),
        ({"app_id": APP_ID, "prompt": "x", "output_format": "webp"}, "output_format"),
        ({"app_id": APP_ID, "prompt": "x", "image_size": "auto"}, "image_size"),
        (
            {"app_id": APP_ID, "prompt": "x", "image_size": {"width": 0, "height": 512}},
            "width",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "x",
                "image_size": {"width": 14143, "height": 512},
            },
            "width",
        ),
        (
            {"app_id": APP_ID, "prompt": "x", "image_size": {"width": 512, "height": 0}},
            "height",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "x",
                "image_size": {"width": 512, "height": 14143},
            },
            "height",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "x",
                "image_size": {"width": 512, "height": 512, "unit": "px"},
            },
            "unit",
        ),
        ({"app_id": APP_ID, "prompt": "x", "num_images": 0}, "num_images"),
        ({"app_id": APP_ID, "prompt": "x", "num_images": 5}, "num_images"),
        ({"app_id": APP_ID, "prompt": "x", "sync_mode": None}, "sync_mode"),
        ({"app_id": APP_ID, "prompt": "x", "unexpected": True}, "unexpected"),
    ],
)
def test_ideogram_v4_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        IdeogramV4Config.model_validate(payload)
