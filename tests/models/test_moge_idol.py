from __future__ import annotations

from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

MOGE_IDS = ("microsoft/moge-2", "microsoft/moge-3")
IDOL_IDS = ("speridlabs/idol", "speridlabs/idol/max", "speridlabs/idol/max/turbo")
MAX_IDS = IDOL_IDS[1:]
IMAGE_URL = "https://example.com/object.png"
MOGE_DEFAULTS = {
    "image_url": "https://storage.googleapis.com/falserverless/example_inputs/dog.png",
    "resolution_level": 9,
    "fov_x": None,
    "apply_mask": True,
    "edge_threshold": 0.04,
    "export_glb": True,
    "export_ply": True,
    "enable_safety_checker": True,
}
IDOL_DEFAULTS = {
    "image_url": IMAGE_URL,
    "image_type": "synthetic",
    "num_gaussians": 262_144,
    "num_inference_steps": 50,
    "guidance_scale": 3,
    "seed": None,
    "enable_safety_checker": True,
}


def validated(app_id: str, **parameters: Any) -> Any:
    if app_id in IDOL_IDS:
        parameters = {"image_url": IMAGE_URL, **parameters}
    config = validate_parameters(app_id, parameters)
    assert config is not None, f"{app_id} must be registered"
    return config


@pytest.mark.parametrize("app_id", (*MOGE_IDS, *IDOL_IDS))
def test_geometry_endpoints_register_defaults_and_discriminator(app_id: str) -> None:
    config = validated(app_id)
    if app_id in MOGE_IDS:
        defaults = dict(MOGE_DEFAULTS)
        defaults.update(
            {"model": "vitl-normal"}
            if app_id == MOGE_IDS[0]
            else {
                "num_refinement_steps": 3,
            }
        )
    else:
        defaults = dict(IDOL_DEFAULTS)
        if app_id in MAX_IDS:
            defaults.update(
                enable_pbr=False,
                rig=False,
                animations=[],
                mesh_resolution=1024,
                enable_usdz=False,
            )
    assert app_id in SUPPORTED_APP_IDS
    assert config.model_dump() == {"app_id": app_id, **defaults}
    assert type(config) is config_class_for_app_id(app_id)
    assert config.random_seed_field == ("seed" if app_id in IDOL_IDS else None)
    routed = TypeAdapter(FalConfig).validate_python(config.model_dump())
    assert type(routed) is type(config)


@pytest.mark.parametrize("app_id", (*MOGE_IDS, *IDOL_IDS))
def test_geometry_endpoints_appear_in_models_and_provide_valid_schema_examples(app_id: str) -> None:
    runner = CliRunner()
    listing = runner.invoke(app, ["models"])
    assert listing.exit_code == 0
    assert app_id in listing.stdout.splitlines()
    example = runner.invoke(app, ["schema", app_id])
    assert example.exit_code == 0
    payload = YAML(typ="safe").load(example.stdout)
    assert payload["app_id"] == app_id
    config = validate_parameters(app_id, payload["parameters"])
    assert config is not None


@pytest.mark.parametrize("app_id", IDOL_IDS)
def test_idol_requires_an_image(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image_url"):
        validate_parameters(app_id, {})


@pytest.mark.parametrize("app_id", MOGE_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resolution_level", 0),
        ("resolution_level", 9),
        ("fov_x", None),
        ("fov_x", 0.01),
        ("fov_x", 179),
        ("edge_threshold", 0),
        ("edge_threshold", 1),
        ("image_url", IMAGE_URL),
        ("apply_mask", False),
        ("export_glb", False),
        ("export_ply", False),
        ("enable_safety_checker", False),
    ],
)
def test_moge_accepts_geometry_options_and_boundaries(app_id: str, field: str, value: Any) -> None:
    assert getattr(validated(app_id, **{field: value}), field) == value


@pytest.mark.parametrize("app_id", MOGE_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resolution_level", -1),
        ("resolution_level", 10),
        ("resolution_level", 1.5),
        ("fov_x", 0),
        ("fov_x", 179.01),
        ("edge_threshold", -0.01),
        ("edge_threshold", 1.01),
        ("image_url", None),
        ("apply_mask", None),
        ("seed", 42),
        ("unexpected", True),
    ],
)
def test_moge_rejects_invalid_geometry_options(app_id: str, field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: value})


@pytest.mark.parametrize("model", ["vitl-normal", "vitl", "vitb-normal", "vits-normal"])
def test_moge_2_accepts_checkpoint_variants(model: str) -> None:
    assert validated(MOGE_IDS[0], model=model).model == model


@pytest.mark.parametrize(
    ("app_id", "parameters", "field"),
    [
        (MOGE_IDS[0], {"model": "unknown"}, "model"),
        (MOGE_IDS[0], {"num_refinement_steps": 3}, "num_refinement_steps"),
        (MOGE_IDS[1], {"model": "vitl"}, "model"),
        (MOGE_IDS[1], {"num_refinement_steps": -1}, "num_refinement_steps"),
        (MOGE_IDS[1], {"num_refinement_steps": 6}, "num_refinement_steps"),
    ],
)
def test_moge_versions_enforce_their_own_parameters(
    app_id: str, parameters: dict[str, Any], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **parameters)


@pytest.mark.parametrize("steps", [0, 5])
def test_moge_3_accepts_refinement_boundaries(steps: int) -> None:
    assert validated(MOGE_IDS[1], num_refinement_steps=steps).num_refinement_steps == steps


@pytest.mark.parametrize("app_id", IDOL_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("image_type", "synthetic"),
        ("image_type", "real"),
        ("num_gaussians", 32_768),
        ("num_gaussians", 32_769),
        ("num_gaussians", 1_048_576),
        ("num_inference_steps", 1),
        ("num_inference_steps", 50),
        ("guidance_scale", 0),
        ("guidance_scale", 10),
        ("seed", None),
        ("seed", -1),
        ("seed", 42),
        ("enable_safety_checker", False),
    ],
)
def test_idol_accepts_sampling_options_and_boundaries(app_id: str, field: str, value: Any) -> None:
    assert getattr(validated(app_id, **{field: value}), field) == value


@pytest.mark.parametrize("app_id", IDOL_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("image_url", None),
        ("image_type", "photo"),
        ("num_gaussians", 32_767),
        ("num_gaussians", 1_048_577),
        ("num_inference_steps", 0),
        ("num_inference_steps", 51),
        ("guidance_scale", -0.01),
        ("guidance_scale", 10.01),
        ("seed", 0.5),
        ("enable_safety_checker", None),
        ("unexpected", True),
    ],
)
def test_idol_rejects_invalid_sampling_options(app_id: str, field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: value})


@pytest.mark.parametrize("app_id", MAX_IDS)
@pytest.mark.parametrize("resolution", [128, 256, 512, 768, 1024, 1536])
def test_idol_max_accepts_mesh_resolutions(app_id: str, resolution: int) -> None:
    config = validated(app_id, mesh_resolution=resolution, enable_pbr=True, enable_usdz=True)
    assert config.mesh_resolution == resolution
    assert config.enable_pbr is True
    assert config.enable_usdz is True


@pytest.mark.parametrize("app_id", MAX_IDS)
def test_idol_max_requires_rigging_for_animations(app_id: str) -> None:
    with pytest.raises(ValidationError, match="animations.*rig"):
        validated(app_id, animations=["walk"])
    with pytest.raises(ValidationError, match="animations.*rig"):
        validated(app_id, rig=False, animations=["idle"])
    config = validated(app_id, rig=True, animations=["walk", "run", "jump", "idle"])
    assert config.rig is True
    assert config.animations == ["walk", "run", "jump", "idle"]
    assert validated(app_id, rig=False, animations=[]).animations == []


@pytest.mark.parametrize("app_id", MAX_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("mesh_resolution", 2048),
        ("mesh_resolution", "1024"),
        ("animations", ["fly"]),
        ("animations", None),
        ("rig", None),
        ("enable_pbr", None),
        ("enable_usdz", None),
    ],
)
def test_idol_max_rejects_invalid_mesh_options(app_id: str, field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{"rig": True, field: value})


@pytest.mark.parametrize(
    "field", ["enable_pbr", "rig", "animations", "mesh_resolution", "enable_usdz"]
)
def test_idol_base_does_not_accept_mesh_only_options(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(IDOL_IDS[0], **{field: None})


def test_idol_max_animation_lists_are_independent() -> None:
    first = validated(MAX_IDS[0], rig=True)
    second = validated(MAX_IDS[1], rig=True)
    first.animations.append("idle")
    assert second.animations == []
