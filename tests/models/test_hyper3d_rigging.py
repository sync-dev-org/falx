from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    Hyper3dRiggingAnimationsConfig,
    Hyper3dRiggingConfig,
    config_class_for_app_id,
    validate_parameters,
)

APP_ID = "hyper3d/rigging"
ANIMATIONS_APP_ID = "hyper3d/rigging/animations"
BONE = {"name": "root", "parent": -1}
CATEGORIES = [
    "human",
    "canine",
    "bird",
    "fish",
    "heavyhooved",
    "leanhooved",
    "lizard",
    "rodentia",
    "seaturtle",
]


def test_rigging_preserves_defaults_and_omits_unspecified_options() -> None:
    config = Hyper3dRiggingConfig(app_id=APP_ID, model_url="mesh")

    assert config.model_dump() == {
        "app_id": APP_ID,
        "model_url": "mesh",
        "skeleton_description": None,
        "bone_template": "auto",
        "geometry_file_format": "fbx",
        "animation_presets": None,
        "hierarchy": None,
        "image_url": None,
        "animation_urls": None,
        "skinning_method": "shell",
        "in_place": False,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        *(("bone_template", v) for v in ["auto", "human", "quadruped", "bird", "dragon", "kaiju"]),
        *(("geometry_file_format", v) for v in ["glb", "fbx", "usdz"]),
        *(("skinning_method", v) for v in ["shell", "core"]),
        ("image_url", "image"),
        ("animation_presets", []),
        ("animation_urls", []),
        ("in_place", True),
    ],
)
def test_rigging_accepts_options(field, value) -> None:
    config = Hyper3dRiggingConfig.model_validate(
        {"app_id": APP_ID, "model_url": "mesh", field: value}
    )

    assert config.model_dump()[field] == value


@pytest.mark.parametrize("bone_count", [1, 256])
def test_custom_skeleton_accepts_bone_count_boundaries(bone_count) -> None:
    bones = [BONE] + [{"name": f"bone{i}", "parent": 0} for i in range(1, bone_count)]
    config = Hyper3dRiggingConfig(
        app_id=APP_ID, model_url="mesh", bone_template="custom", hierarchy=bones
    )

    assert len(config.hierarchy) == bone_count
    assert config.hierarchy[0].name == "root"
    assert config.hierarchy[0].length is None


def test_custom_skeleton_accepts_description_instead_of_hierarchy() -> None:
    config = Hyper3dRiggingConfig(
        app_id=APP_ID, model_url="mesh", bone_template="custom", skeleton_description="Four legs"
    )

    assert config.skeleton_description == "Four legs"
    assert config.hierarchy is None


def test_custom_skeleton_preserves_bone_transform_and_positive_length() -> None:
    bone = {**BONE, "transform": [1.0, 0.0, 0.5], "length": 0.01}
    config = Hyper3dRiggingConfig(
        app_id=APP_ID, model_url="mesh", bone_template="custom", hierarchy=[bone]
    )

    assert config.hierarchy[0].model_dump() == bone


@pytest.mark.parametrize("field", ["animation_presets", "animation_urls"])
def test_rigging_accepts_ten_animation_entries(field) -> None:
    values = [f"https://example.com/{i}.fbx" for i in range(10)]
    config = Hyper3dRiggingConfig.model_validate(
        {"app_id": APP_ID, "model_url": "mesh", field: values}
    )

    assert config.model_dump()[field] == values


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "model_url"),
        ({"model_url": ""}, "model_url"),
        ({"image_url": ""}, "image_url"),
        ({"geometry_file_format": "obj"}, "geometry_file_format"),
        ({"bone_template": "fish"}, "bone_template"),
        ({"skinning_method": "other"}, "skinning_method"),
        ({"bone_template": "custom"}, "custom"),
        ({"hierarchy": [BONE]}, "custom"),
        ({"skeleton_description": "Four legs"}, "custom"),
        (
            {"bone_template": "custom", "hierarchy": [BONE], "skeleton_description": "Legs"},
            "exactly one",
        ),
        ({"bone_template": "custom", "hierarchy": []}, "hierarchy"),
        ({"bone_template": "custom", "hierarchy": [BONE] * 257}, "hierarchy"),
        ({"bone_template": "custom", "skeleton_description": " \n"}, "skeleton_description"),
        ({"animation_presets": ["walk"] * 11}, "animation_presets"),
        ({"animation_presets": ["walk", "walk"]}, "distinct"),
        ({"animation_urls": ["clip"] * 11}, "animation_urls"),
        ({"animation_urls": [""]}, "animation_urls"),
        ({"animation_urls": ["clip"], "animation_presets": ["walk"]}, "mutually exclusive"),
        ({"animation_urls": ["clip"], "in_place": True}, "in_place"),
        ({"in_place": None}, "in_place"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_rigging_rejects_invalid_parameters(parameters, needle) -> None:
    payload = {"app_id": APP_ID, "model_url": "mesh", **parameters}
    if not parameters:
        payload.pop("model_url")
    with pytest.raises(ValidationError, match=needle):
        Hyper3dRiggingConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("bone", "needle"),
    [
        ({"parent": -1}, "name"),
        ({"name": "root"}, "parent"),
        ({**BONE, "name": ""}, "name"),
        ({**BONE, "name": " \t"}, "name"),
        ({**BONE, "parent": -2}, "parent"),
        ({**BONE, "length": 0}, "length"),
        ({**BONE, "length": -1}, "length"),
        ({**BONE, "length": None}, "length"),
        ({**BONE, "transform": ["bad"]}, "transform"),
        ({**BONE, "unexpected": True}, "unexpected"),
    ],
)
def test_custom_skeleton_rejects_invalid_bones(bone, needle) -> None:
    with pytest.raises(ValidationError, match=needle):
        Hyper3dRiggingConfig(
            app_id=APP_ID, model_url="mesh", bone_template="custom", hierarchy=[bone]
        )


@pytest.mark.parametrize("category", [None, *CATEGORIES])
def test_animation_catalog_accepts_all_categories(category) -> None:
    config = Hyper3dRiggingAnimationsConfig(app_id=ANIMATIONS_APP_ID, category=category)

    assert config.category == category


def test_animation_catalog_defaults_to_all_categories_and_rejects_unknown_category() -> None:
    assert Hyper3dRiggingAnimationsConfig(app_id=ANIMATIONS_APP_ID).category is None
    with pytest.raises(ValidationError, match="category"):
        Hyper3dRiggingAnimationsConfig(app_id=ANIMATIONS_APP_ID, category="unknown")


@pytest.mark.parametrize(
    "app_id",
    [
        "hyper3d/lowpoly/image-to-3d",
        "hyper3d/lowpoly/mesh-to-3d",
        "hyper3d/lowpoly/text-to-3d",
        APP_ID,
        ANIMATIONS_APP_ID,
    ],
)
def test_hyper3d_registration_models_listing_and_schema_example(app_id) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class.random_seed_field is None
    runner = CliRunner()
    models = runner.invoke(app, ["models"])
    assert models.exit_code == 0
    assert app_id in models.stdout.splitlines()
    schema = runner.invoke(app, ["schema", app_id])
    assert schema.exit_code == 0
    example = YAML(typ="safe").load(schema.stdout)
    config = validate_parameters(app_id, example["parameters"])
    assert isinstance(config, config_class)
