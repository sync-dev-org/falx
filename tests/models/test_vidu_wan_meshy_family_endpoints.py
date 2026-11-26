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

VIDU_TEXT = "fal-ai/vidu/q3/text-to-video/turbo"
VIDU_IMAGE = "fal-ai/vidu/q3/image-to-video/turbo"
WAN_TEXT = "alibaba/wan-3.0/text-to-video"
WAN_IMAGE = "alibaba/wan-3.0/image-to-video"
WAN_REFERENCE = "alibaba/wan-3.0/reference-to-video"
MESHY_IMAGE = "meshy/v7/image-to-3d"
MESHY_RETEXTURE = "meshy/v7/retexture"

WAN_DEFAULTS = {
    "resolution": "1080p",
    "aspect_ratio": "adaptive",
    "duration": 5,
    "audio": True,
    "enable_prompt_expansion": True,
    "enable_thinking": False,
    "seed": None,
    "enable_safety_checker": True,
}
CASES = [
    (
        VIDU_TEXT,
        {"prompt": "A quiet park."},
        {
            "duration": 5,
            "seed": None,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "audio": True,
            "enable_safety_checker": True,
        },
        "seed",
    ),
    (
        VIDU_IMAGE,
        {"image_url": "https://example.com/input.png"},
        {
            "prompt": "",
            "end_image_url": None,
            "duration": 5,
            "seed": None,
            "resolution": "720p",
            "audio": True,
            "enable_safety_checker": True,
        },
        "seed",
    ),
    (WAN_TEXT, {"prompt": "A quiet park."}, WAN_DEFAULTS, "seed"),
    (
        WAN_IMAGE,
        {"start_image_url": "https://example.com/input.png"},
        {**WAN_DEFAULTS, "prompt": None, "end_image_url": None},
        "seed",
    ),
    (
        WAN_REFERENCE,
        {},
        {
            **WAN_DEFAULTS,
            "prompt": None,
            "reference_image_urls": [],
            "reference_video_urls": [],
            "reference_audio_urls": [],
            "file_url": None,
            "web_url": None,
        },
        "seed",
    ),
    (
        MESHY_IMAGE,
        {"image_url": "https://example.com/input.png"},
        {
            "model_type": "standard",
            "topology": "triangle",
            "target_polycount": 30_000,
            "symmetry_mode": "auto",
            "should_remesh": True,
            "should_texture": True,
            "texture_model": None,
            "enable_pbr": False,
            "is_a_t_pose": False,
            "pose_mode": "",
            "texture_prompt": None,
            "texture_image_url": None,
            "enable_rigging": False,
            "rigging_height_meters": 1.7,
            "skeleton_template": None,
            "include_fingers": False,
            "enable_animation": False,
            "animation_action_id": 92,
            "enable_safety_checker": True,
            "geometry_resolution": None,
            "ultra_mode": False,
        },
        None,
    ),
    (
        MESHY_RETEXTURE,
        {"model_url": "https://example.com/model.glb", "text_style_prompt": "Painted wood."},
        {
            "image_style_url": None,
            "texture_resolution": "2k",
            "enable_original_uv": True,
            "enable_pbr": False,
            "enable_safety_checker": True,
        },
        None,
    ),
]
MINIMUM = {app_id: parameters for app_id, parameters, _, _ in CASES}


def validated(app_id: str, **parameters: Any) -> Any:
    config = validate_parameters(app_id, {**MINIMUM[app_id], **parameters})
    assert config is not None, f"{app_id} must be registered"
    return config


@pytest.mark.parametrize(("app_id", "parameters", "defaults", "seed_field"), CASES)
def test_family_endpoints_validate_defaults_and_route_to_registered_classes(
    app_id: str,
    parameters: dict[str, Any],
    defaults: dict[str, Any],
    seed_field: str | None,
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config = validated(app_id)
    assert config.model_dump() == {"app_id": app_id, **defaults, **parameters}
    assert type(config) is config_class_for_app_id(app_id)
    assert config.random_seed_field == seed_field
    routed = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters})
    assert type(routed) is type(config)


@pytest.mark.parametrize("app_id", MINIMUM)
def test_models_command_lists_family_endpoints(app_id: str) -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert app_id in result.stdout.splitlines()


@pytest.mark.parametrize(("app_id", "parameters", "defaults", "seed_field"), CASES)
def test_schema_command_prints_family_job_yaml(
    app_id: str,
    parameters: dict[str, Any],
    defaults: dict[str, Any],
    seed_field: str | None,
) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    required_examples = {
        key: "<your prompt here>" if key == "prompt" else "https://example.com/input"
        for key in parameters
        if key != "text_style_prompt"
    }
    if app_id == MESHY_RETEXTURE:
        required_examples["text_style_prompt"] = "<your prompt here>"
    assert payload["parameters"] == {**defaults, **required_examples}


@pytest.mark.parametrize(
    ("app_id", "required"),
    [
        (VIDU_TEXT, "prompt"),
        (VIDU_IMAGE, "image_url"),
        (WAN_TEXT, "prompt"),
        (WAN_IMAGE, "start_image_url"),
        (MESHY_IMAGE, "image_url"),
        (MESHY_RETEXTURE, "model_url"),
    ],
)
def test_family_endpoints_reject_missing_required_input(app_id: str, required: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    parameters = {key: value for key, value in MINIMUM[app_id].items() if key != required}
    with pytest.raises(ValidationError, match=required):
        config_class.model_validate({"app_id": app_id, **parameters})


@pytest.mark.parametrize("app_id", MINIMUM)
def test_family_endpoints_reject_unknown_parameters(app_id: str) -> None:
    with pytest.raises(ValidationError, match="unexpected"):
        validated(app_id, unexpected=True)


@pytest.mark.parametrize("app_id", [VIDU_TEXT, VIDU_IMAGE])
@pytest.mark.parametrize("duration", [1, 16])
def test_vidu_turbo_accepts_duration_and_prompt_boundaries(app_id: str, duration: int) -> None:
    config = validated(app_id, duration=duration, prompt="p" * 2000, seed=-1)
    assert config.duration == duration
    assert len(config.prompt) == 2000
    assert config.seed == -1


@pytest.mark.parametrize("app_id", [VIDU_TEXT, VIDU_IMAGE])
@pytest.mark.parametrize("resolution", ["360p", "540p", "720p", "1080p"])
def test_vidu_turbo_accepts_resolution_options(app_id: str, resolution: str) -> None:
    assert validated(app_id, resolution=resolution).resolution == resolution


@pytest.mark.parametrize("aspect_ratio", ["16:9", "9:16", "4:3", "3:4", "1:1"])
def test_vidu_turbo_text_accepts_aspect_ratios(aspect_ratio: str) -> None:
    assert validated(VIDU_TEXT, aspect_ratio=aspect_ratio).aspect_ratio == aspect_ratio


@pytest.mark.parametrize("app_id", [VIDU_TEXT, VIDU_IMAGE])
@pytest.mark.parametrize(
    ("field", "value"),
    [("duration", 0), ("duration", 17), ("prompt", "p" * 2001), ("resolution", "4k")],
)
def test_vidu_turbo_rejects_invalid_video_parameters(app_id: str, field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: value})


def test_vidu_turbo_preserves_transition_and_nullable_screening_rules() -> None:
    assert validated(VIDU_IMAGE, enable_safety_checker=None).enable_safety_checker is None
    assert validated(VIDU_TEXT, enable_safety_checker=False).enable_safety_checker is False
    with pytest.raises(ValidationError, match="enable_safety_checker"):
        validated(VIDU_TEXT, enable_safety_checker=None)
    with pytest.raises(ValidationError, match="360p"):
        validated(VIDU_IMAGE, end_image_url="https://example.com/end.png", resolution="360p")
    assert validated(VIDU_IMAGE, end_image_url="https://example.com/end.png").resolution == "720p"
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validated(VIDU_TEXT, aspect_ratio="auto")


@pytest.mark.parametrize("app_id", [WAN_TEXT, WAN_IMAGE, WAN_REFERENCE])
def test_wan_accepts_20000_character_prompts_and_rejects_longer_prompts(app_id: str) -> None:
    assert len(validated(app_id, prompt="p" * 20_000).prompt) == 20_000
    with pytest.raises(ValidationError, match="prompt"):
        validated(app_id, prompt="p" * 20_001)


@pytest.mark.parametrize("app_id", [WAN_TEXT, WAN_IMAGE, WAN_REFERENCE])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", None),
        ("duration", 2),
        ("duration", 30),
        ("seed", None),
        ("seed", 0),
        ("seed", 2_147_483_647),
        *(("resolution", value) for value in ["480p", "720p", "1080p"]),
        *(("aspect_ratio", value) for value in ["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16"]),
    ],
)
def test_wan_accepts_video_options_and_bounds(app_id: str, field: str, value: Any) -> None:
    assert getattr(validated(app_id, **{field: value}), field) == value


@pytest.mark.parametrize("app_id", [WAN_TEXT, WAN_IMAGE, WAN_REFERENCE])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 1),
        ("duration", 31),
        ("seed", -1),
        ("seed", 2_147_483_648),
        ("resolution", "4k"),
        ("aspect_ratio", "21:9"),
    ],
)
def test_wan_rejects_invalid_video_options(app_id: str, field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(app_id, **{field: value})


def test_wan_text_requires_nonempty_prompt_but_media_prompts_are_nullable() -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validated(WAN_TEXT, prompt="")
    for app_id in [WAN_IMAGE, WAN_REFERENCE]:
        assert validated(app_id, prompt=None).prompt is None
        assert validated(app_id, prompt="").prompt == ""


@pytest.mark.parametrize(
    ("field", "limit"),
    [
        ("reference_image_urls", 10),
        ("reference_video_urls", 5),
        ("reference_audio_urls", 5),
    ],
)
def test_wan_reference_limits_media_counts(field: str, limit: int) -> None:
    urls = ["https://example.com/media"] * limit
    assert getattr(validated(WAN_REFERENCE, **{field: urls}), field) == urls
    with pytest.raises(ValidationError, match=field):
        validated(WAN_REFERENCE, **{field: [*urls, "https://example.com/extra"]})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_type", "standard"),
        ("topology", "quad"),
        ("topology", "triangle"),
        *(("symmetry_mode", value) for value in ["off", "auto", "on"]),
        *(("pose_mode", value) for value in ["", "a-pose", "t-pose"]),
        *(("texture_model", value) for value in [None, "meshy-7", "meshy-n1", "meshy-6-lite"]),
        *(("geometry_resolution", value) for value in [None, "standard", "2k"]),
        *(
            ("skeleton_template", value)
            for value in [
                None,
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
        ),
        ("target_polycount", 100),
        ("target_polycount", 300_000),
        ("rigging_height_meters", 0.1),
        ("texture_prompt", "p" * 800),
    ],
)
def test_meshy_image_accepts_options_and_bounds(field: str, value: Any) -> None:
    assert getattr(validated(MESHY_IMAGE, **{field: value}), field) == value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_type", "lowpoly"),
        ("topology", "ngon"),
        ("symmetry_mode", "mirror"),
        ("pose_mode", "standing"),
        ("texture_model", "meshy-6"),
        ("geometry_resolution", "4k"),
        ("skeleton_template", "unknown"),
        ("target_polycount", 99),
        ("target_polycount", 300_001),
        ("rigging_height_meters", 0),
        ("texture_prompt", "p" * 801),
        ("seed", 42),
    ],
)
def test_meshy_image_rejects_invalid_parameters(field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(MESHY_IMAGE, **{field: value})


@pytest.mark.parametrize("texture_resolution", ["2k", "4k", "8k"])
def test_meshy_retexture_accepts_style_sources_and_resolution(texture_resolution: str) -> None:
    config = validated(
        MESHY_RETEXTURE,
        text_style_prompt="p" * 800,
        image_style_url="https://example.com/style.webp",
        texture_resolution=texture_resolution,
    )
    assert config.texture_resolution == texture_resolution
    assert len(config.text_style_prompt) == 800
    assert config.image_style_url == "https://example.com/style.webp"
    assert (
        validated(
            MESHY_RETEXTURE,
            text_style_prompt=None,
            image_style_url="data:image/png;base64,AA==",
        ).text_style_prompt
        is None
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("text_style_prompt", "p" * 801),
        ("texture_resolution", "1k"),
        ("seed", 42),
    ],
)
def test_meshy_retexture_rejects_invalid_parameters(field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        validated(MESHY_RETEXTURE, **{field: value})


def test_meshy_retexture_requires_a_style_source() -> None:
    with pytest.raises(ValidationError, match="text_style_prompt.*image_style_url"):
        validated(MESHY_RETEXTURE, text_style_prompt=None, image_style_url=None)
