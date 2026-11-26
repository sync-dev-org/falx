from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    MeshyV7TextTo3dConfig,
    Vggt1bConfig,
    config_class_for_app_id,
)

APP_IDS = {"fal-ai/vggt-1b", "meshy/v7/text-to-3d"}

runner = CliRunner()
safe_yaml = YAML(typ="safe")


def test_3d_app_ids_are_registered() -> None:
    assert APP_IDS <= SUPPORTED_APP_IDS
    assert config_class_for_app_id("meshy/v7/text-to-3d") is MeshyV7TextTo3dConfig
    assert config_class_for_app_id("fal-ai/vggt-1b") is Vggt1bConfig


def test_3d_configs_declare_seed_metadata() -> None:
    assert MeshyV7TextTo3dConfig.random_seed_field == "seed"
    assert Vggt1bConfig.random_seed_field is None


def test_models_command_lists_3d_app_ids() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(result.stdout.splitlines()) >= APP_IDS


@pytest.mark.parametrize(
    ("app_id", "expected_parameters"),
    [
        (
            "meshy/v7/text-to-3d",
            {
                "prompt": "<your prompt here>",
                "mode": "full",
                "seed": None,
                "model_type": "standard",
                "topology": "triangle",
                "target_polycount": 30_000,
                "should_remesh": True,
                "symmetry_mode": "auto",
                "enable_pbr": False,
                "is_a_t_pose": False,
                "pose_mode": "",
                "enable_prompt_expansion": False,
                "texture_prompt": None,
                "texture_image_url": None,
                "enable_rigging": False,
                "rigging_height_meters": 1.7,
                "enable_animation": False,
                "animation_action_id": 92,
                "enable_safety_checker": True,
                "ultra_mode": False,
            },
        ),
        (
            "fal-ai/vggt-1b",
            {
                "image_urls": [],
                "video_url": None,
                "frame_sampling_rate": 24,
                "alpha_blend_onto": "white",
                "export_prediction_data": True,
                "export_depth_maps": True,
                "export_point_cloud": True,
                "array_encoding": "base64",
                "exclude_keys": [],
                "confidence_percentile": 50,
                "max_points": 250_000,
                "enable_safety_checker": True,
            },
        ),
    ],
)
def test_schema_command_prints_3d_api_fields(
    app_id: str,
    expected_parameters: dict[str, object],
) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"] == expected_parameters
