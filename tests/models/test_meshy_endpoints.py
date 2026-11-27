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

URL = "https://example.com/input"
IMAGE_APPS = ["meshy/t2/image-to-3d", "meshy/t2.5/image-to-3d"]
TEXT_APPS = ["meshy/t2/text-to-3d", "meshy/t2.5/text-to-3d"]
SMART_APPS = IMAGE_APPS + TEXT_APPS
RETEXTURE_APPS = ["meshy/v6/retexture", "meshy/v6-lite/retexture"]
RIG = "meshy/rigging"
MULTI = "meshy/rigging/multi-animation"
N1 = "meshy/n1/retexture"
RELIEF = "meshy/relief"
SKELETONS = [
    "mixamo",
    "ue5_mannequin",
    "unity_humanoid",
    "maya_human_ik",
    "blender_rigify_basic_human",
    "max_biped",
    "cc5_hd_neutral_base",
    "daz_genesis9",
    "meshyrig",
]
RIG_DEFAULTS = {
    "skeleton_template": None,
    "include_fingers": False,
    "enable_safety_checker": True,
}
SMART_DEFAULTS = {
    **RIG_DEFAULTS,
    "target_polycount": 4000,
    "enable_rigging": False,
    "rigging_height_meters": 1.7,
    "enable_animation": False,
    "animation_action_id": 92,
    "enable_pbr": False,
    "pose_mode": "",
    "texture_prompt": None,
    "texture_image_url": None,
}
MINIMUM = {
    **{app_id: {"image_url": URL} for app_id in IMAGE_APPS},
    **{app_id: {"prompt": "A carved owl."} for app_id in TEXT_APPS},
    **{
        app_id: {"model_url": URL, "text_style_prompt": "Painted wood."}
        for app_id in RETEXTURE_APPS
    },
    RIG: {"model_url": URL},
    MULTI: {"model_url": URL, "animation_action_ids": [36, 92]},
    N1: {"model_url": URL, "image_style_url": URL},
    RELIEF: {"image_url": URL},
}
DEFAULTS = {
    **{
        app_id: {
            **SMART_DEFAULTS,
            "target_polycount": 15_000 if "/t2.5/" in app_id else 4000,
            "should_texture": True,
            "texture_model": "default",
        }
        for app_id in IMAGE_APPS
    },
    **{
        app_id: {
            **SMART_DEFAULTS,
            "target_polycount": 15_000 if "/t2.5/" in app_id else 4000,
            "mode": "full",
            "seed": None,
            "enable_prompt_expansion": False,
            "texture_model": "meshy-7.1",
        }
        for app_id in TEXT_APPS
    },
    **{
        app_id: {
            "image_style_url": None,
            "texture_resolution": "2k",
            "enable_original_uv": True,
            "enable_pbr": False,
            "enable_safety_checker": True,
        }
        for app_id in RETEXTURE_APPS
    },
    RIG: {
        **RIG_DEFAULTS,
        "height_meters": 1.7,
        "enable_animation": False,
        "animation_action_id": 92,
    },
    MULTI: {**RIG_DEFAULTS, "height_meters": 1.7},
    N1: {
        "enable_original_uv": True,
        "multiview_image_urls": None,
        "enable_safety_checker": True,
    },
    RELIEF: {
        "variant": "low",
        "should_generate_model": True,
        "size_mm": 60,
        "carving_mode": "emboss",
        "carving_depth_mm": None,
        "remove_base": False,
        "removal_threshold": None,
        "base_thickness_mm": None,
        "bend_mode": "off",
        "bend_axis": "xz",
        "bend_angle": 60,
        "mesh_resolution": 1024,
        "enable_safety_checker": True,
    },
}


def validated(app_id: str, **parameters: Any) -> Any:
    config = validate_parameters(app_id, {**MINIMUM[app_id], **parameters})
    assert config is not None, f"{app_id} must be registered"
    return config


@pytest.mark.parametrize("app_id", MINIMUM)
def test_meshy_endpoints_route_with_documented_defaults(app_id: str) -> None:
    config = validated(app_id)
    assert config.model_dump() == {"app_id": app_id, **DEFAULTS[app_id], **MINIMUM[app_id]}
    assert type(config) is config_class_for_app_id(app_id)
    assert type(TypeAdapter(FalConfig).validate_python(config.model_dump())) is type(config)
    assert config.random_seed_field == ("seed" if app_id in TEXT_APPS else None)


@pytest.mark.parametrize("app_id", MINIMUM)
def test_meshy_endpoints_appear_in_models_and_have_valid_schema_examples(app_id: str) -> None:
    runner = CliRunner()
    assert app_id in SUPPORTED_APP_IDS
    models = runner.invoke(app, ["models"])
    assert models.exit_code == 0
    assert app_id in models.stdout.splitlines()
    schema = runner.invoke(app, ["schema", app_id])
    assert schema.exit_code == 0
    payload = YAML(typ="safe").load(schema.stdout)
    assert validate_parameters(app_id, payload["parameters"]) is not None


@pytest.mark.parametrize(
    ("app_id", "field"),
    [
        *((app_id, "image_url") for app_id in IMAGE_APPS),
        *((app_id, "prompt") for app_id in TEXT_APPS),
        *((app_id, "model_url") for app_id in RETEXTURE_APPS + [RIG, MULTI, N1]),
        (MULTI, "animation_action_ids"),
        (RELIEF, "image_url"),
    ],
)
def test_meshy_endpoints_reject_missing_required_input(app_id: str, field: str) -> None:
    parameters = {key: value for key, value in MINIMUM[app_id].items() if key != field}
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", MINIMUM)
def test_meshy_endpoints_reject_unknown_parameters(app_id: str) -> None:
    with pytest.raises(ValidationError, match="unexpected"):
        validated(app_id, unexpected=True)


@pytest.mark.parametrize(
    ("app_id", "field", "choices"),
    [
        *((app_id, "pose_mode", ["a-pose", "t-pose", ""]) for app_id in SMART_APPS),
        *(
            (app_id, "skeleton_template", [None, *SKELETONS])
            for app_id in SMART_APPS + [RIG, MULTI]
        ),
        *((app_id, "mode", ["preview", "full"]) for app_id in TEXT_APPS),
        *((app_id, "texture_model", ["meshy-7.1", "meshy-n1"]) for app_id in TEXT_APPS),
        *(
            (app_id, "texture_model", ["default", "meshy-7", "meshy-n1", "meshy-6-lite"])
            for app_id in IMAGE_APPS
        ),
        *((app_id, "texture_resolution", ["2k", "4k", "8k"]) for app_id in RETEXTURE_APPS),
        (RELIEF, "variant", ["low", "high"]),
        (RELIEF, "carving_mode", ["emboss", "engrave"]),
        (RELIEF, "bend_mode", ["off", "convex", "concave"]),
        (RELIEF, "bend_axis", ["xz", "yz"]),
    ],
)
def test_meshy_endpoints_accept_enum_values_and_reject_unknown_options(
    app_id: str, field: str, choices: list[Any]
) -> None:
    for choice in choices:
        parameters = {field: choice}
        if app_id in TEXT_APPS and field == "texture_model" and choice == "meshy-n1":
            parameters["texture_image_url"] = URL
        assert getattr(validated(app_id, **parameters), field) == choice
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: "unknown"})


@pytest.mark.parametrize(
    ("app_id", "field", "low", "high"),
    [
        *((app_id, "target_polycount", 100, 15_000) for app_id in SMART_APPS if "/t2/" in app_id),
        *((app_id, "target_polycount", 100, 30_000) for app_id in SMART_APPS if "/t2.5/" in app_id),
        (RELIEF, "size_mm", 20, 250),
        (RELIEF, "carving_depth_mm", 0, 60),
        (RELIEF, "removal_threshold", 0.01, 1),
        (RELIEF, "base_thickness_mm", 0.1, 10),
        (RELIEF, "bend_angle", 0, 360),
        (RELIEF, "mesh_resolution", 512, 2048),
    ],
)
def test_meshy_endpoints_enforce_numeric_bounds(
    app_id: str, field: str, low: float, high: float
) -> None:
    for value in [low, high]:
        assert getattr(validated(app_id, **{field: value}), field) == value
    for value in [low - 1, high + 1]:
        with pytest.raises(ValidationError, match=field):
            validated(app_id, **{field: value})


@pytest.mark.parametrize("app_id", SMART_APPS + [RIG, MULTI])
def test_meshy_rigging_requires_positive_height(app_id: str) -> None:
    field = "rigging_height_meters" if app_id in SMART_APPS else "height_meters"
    assert getattr(validated(app_id, **{field: 0.1}), field) == 0.1
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: 0})


@pytest.mark.parametrize("app_id", SMART_APPS + [RIG])
def test_meshy_checks_action_range_only_when_animation_is_enabled(app_id: str) -> None:
    parameters = {"enable_rigging": True} if app_id in SMART_APPS else {}
    for action in [0, 696]:
        assert (
            validated(
                app_id, **parameters, enable_animation=True, animation_action_id=action
            ).animation_action_id
            == action
        )
    for action in [-1, 697]:
        with pytest.raises(ValidationError, match="animation_action_id"):
            validated(app_id, **parameters, enable_animation=True, animation_action_id=action)
        assert validated(app_id, animation_action_id=action).animation_action_id == action


@pytest.mark.parametrize("app_id", SMART_APPS)
def test_meshy_smart_topology_animation_requires_rigging(app_id: str) -> None:
    with pytest.raises(ValidationError, match="enable_rigging"):
        validated(app_id, enable_animation=True)


@pytest.mark.parametrize(
    ("app_id", "field", "limit"),
    [
        *((app_id, "prompt", 600) for app_id in TEXT_APPS),
        *((app_id, "texture_prompt", 800) for app_id in SMART_APPS),
        *((app_id, "text_style_prompt", 800) for app_id in RETEXTURE_APPS),
    ],
)
def test_meshy_endpoints_enforce_prompt_lengths(app_id: str, field: str, limit: int) -> None:
    assert getattr(validated(app_id, **{field: "p" * limit}), field) == "p" * limit
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: "p" * (limit + 1)})


@pytest.mark.parametrize("app_id", TEXT_APPS)
def test_meshy_smart_text_texture_sources_are_exclusive_in_full_mode(app_id: str) -> None:
    with pytest.raises(ValidationError, match="texture_prompt.*texture_image_url"):
        validated(app_id, texture_prompt="wood", texture_image_url=URL)
    assert (
        validated(app_id, mode="preview", texture_prompt="wood", texture_image_url=URL).mode
        == "preview"
    )
    assert validated(app_id, seed=-1).seed == -1


@pytest.mark.parametrize("app_id", SMART_APPS)
def test_meshy_n1_texturing_requires_image_guidance_and_disallows_text_and_pbr(app_id: str) -> None:
    parameters = {"texture_model": "meshy-n1", "texture_image_url": URL}
    assert validated(app_id, **parameters).texture_model == "meshy-n1"
    for extra in [{"texture_prompt": "wood"}, {"enable_pbr": True}]:
        with pytest.raises(ValidationError, match="meshy-n1"):
            validated(app_id, **parameters, **extra)
    if app_id in TEXT_APPS:
        with pytest.raises(ValidationError, match="texture_image_url"):
            validated(app_id, texture_model="meshy-n1")
        assert validated(app_id, mode="preview", texture_model="meshy-n1").mode == "preview"
    else:
        assert validated(app_id, texture_model="meshy-n1").texture_image_url is None
        assert (
            validated(
                app_id, should_texture=False, texture_model="meshy-n1", enable_pbr=True
            ).enable_pbr
            is True
        )


@pytest.mark.parametrize("app_id", RETEXTURE_APPS)
def test_meshy_retexture_requires_a_style_source_and_allows_both(app_id: str) -> None:
    with pytest.raises(ValidationError, match="text_style_prompt.*image_style_url"):
        validated(app_id, text_style_prompt=None)
    assert validated(app_id, text_style_prompt=None, image_style_url=URL).image_style_url == URL
    assert validated(app_id, image_style_url=URL).text_style_prompt == "Painted wood."


def test_meshy_n1_retexture_requires_exactly_one_reference_source() -> None:
    with pytest.raises(ValidationError, match="image_style_url.*multiview_image_urls"):
        validated(N1, image_style_url=None)
    with pytest.raises(ValidationError, match="image_style_url.*multiview_image_urls"):
        validated(N1, multiview_image_urls=[URL])
    for count in [1, 4]:
        assert (
            validated(
                N1, image_style_url=None, multiview_image_urls=[URL] * count
            ).multiview_image_urls
            == [URL] * count
        )
    for count in [0, 5]:
        with pytest.raises(ValidationError, match="multiview_image_urls"):
            validated(N1, image_style_url=None, multiview_image_urls=[URL] * count)


def test_meshy_multi_animation_checks_ids_and_distinct_clip_count() -> None:
    assert validated(MULTI, animation_action_ids=[0, 696]).animation_action_ids == [0, 696]
    assert validated(MULTI, animation_action_ids=list(range(10))).animation_action_ids == list(
        range(10)
    )
    duplicates = [92] * 11
    assert validated(MULTI, animation_action_ids=duplicates).animation_action_ids == duplicates
    for actions in [[], [-1], [697], list(range(11))]:
        with pytest.raises(ValidationError, match="animation_action_ids"):
            validated(MULTI, animation_action_ids=actions)


@pytest.mark.parametrize("app_id", [RIG, MULTI])
def test_meshy_standalone_rigging_rejects_empty_model_urls(app_id: str) -> None:
    with pytest.raises(ValidationError, match="model_url"):
        validated(app_id, model_url="")


def test_meshy_relief_disallows_base_thickness_when_the_base_is_removed() -> None:
    with pytest.raises(ValidationError, match="base_thickness_mm.*remove_base"):
        validated(RELIEF, remove_base=True, base_thickness_mm=1)
    assert validated(RELIEF, remove_base=True).base_thickness_mm is None
    assert validated(RELIEF, should_generate_model=False).should_generate_model is False
