from __future__ import annotations

from typing import Any

import pytest
from pydantic import TypeAdapter
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

ROUTES = [
    ("blackforestlabs/flux-3-max/text-to-video", "Flux3MaxTextToVideoConfig", {}),
    (
        "blackforestlabs/flux-3-max/image-to-video",
        "Flux3MaxImageToVideoConfig",
        {"image_url": "https://example.com/a.png"},
    ),
    (
        "blackforestlabs/flux-3-max/keyframes-to-video",
        "Flux3MaxKeyframesToVideoConfig",
        {"keyframes": [{"image_url": "https://example.com/a.png", "frame_index": 0}]},
    ),
    (
        "xai/grok-imagine-video/v1.5/lite/text-to-video",
        "GrokImagineVideoV15LiteTextToVideoConfig",
        {},
    ),
    (
        "xai/grok-imagine-video/v1.5/lite/image-to-video",
        "GrokImagineVideoV15LiteImageToVideoConfig",
        {"image_url": "https://example.com/a.png"},
    ),
    ("heygen/heygen-video/text-to-video", "HeygenVideoTextToVideoConfig", {}),
    (
        "heygen/heygen-video/image-to-video",
        "HeygenVideoImageToVideoConfig",
        {"image_url": "https://example.com/a.png"},
    ),
    ("heygen/heygen-video/reference-to-video", "HeygenVideoReferenceToVideoConfig", {}),
    (
        "tbc/mischief-1/image-to-video",
        "Mischief1ImageToVideoConfig",
        {"image_url": "https://example.com/a.png"},
    ),
]


@pytest.mark.parametrize(("app_id", "class_name", "inputs"), ROUTES)
def test_video_generation_routes_are_registered_and_discriminated(
    app_id: str, class_name: str, inputs: dict[str, Any]
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class.__name__ == class_name
    parsed = TypeAdapter(FalConfig).validate_python(
        {
            "app_id": app_id,
            "prompt": "A forest.",
            **inputs,
        }
    )
    assert type(parsed) is config_class
    assert parsed.model_dump()["app_id"] == app_id


@pytest.mark.parametrize(("app_id", "class_name", "inputs"), ROUTES)
def test_video_generation_schema_prints_valid_job_example(
    app_id: str, class_name: str, inputs: dict[str, Any]
) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    job = YAML(typ="safe").load(result.stdout)
    assert job["app_id"] == app_id
    assert job["iterations"] == 1
    config = validate_parameters(app_id, job["parameters"])
    assert config is not None
    assert type(config).__name__ == class_name


def test_video_generation_models_lists_all_routes() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert {app_id for app_id, _, _ in ROUTES} <= set(result.stdout.splitlines())
