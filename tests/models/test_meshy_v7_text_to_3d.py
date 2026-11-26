from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import MeshyV7TextTo3dConfig

APP_ID = "meshy/v7/text-to-3d"


def test_meshy_v7_text_to_3d_accepts_schema_defaults() -> None:
    config = MeshyV7TextTo3dConfig(app_id=APP_ID, prompt="A carved wooden owl.")

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "A carved wooden owl.",
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
    }


def test_meshy_v7_text_to_3d_accepts_all_fields_at_boundaries() -> None:
    config = MeshyV7TextTo3dConfig(
        app_id=APP_ID,
        prompt="p" * 600,
        mode="preview",
        seed=42,
        model_type="smart-topology",
        topology="quad",
        target_polycount=300_000,
        should_remesh=False,
        symmetry_mode="on",
        enable_pbr=True,
        is_a_t_pose=True,
        pose_mode="t-pose",
        enable_prompt_expansion=True,
        texture_prompt="t" * 600,
        texture_image_url="https://example.com/texture.png",
        enable_rigging=True,
        rigging_height_meters=0.1,
        enable_animation=True,
        animation_action_id=0,
        enable_safety_checker=False,
        ultra_mode=True,
    )

    assert config.prompt == "p" * 600
    assert config.model_type == "smart-topology"
    assert config.target_polycount == 300_000
    assert config.rigging_height_meters == 0.1
    assert config.animation_action_id == 0


def test_meshy_v7_text_to_3d_preserves_required_defaults_and_bounds_in_schema() -> None:
    schema = MeshyV7TextTo3dConfig.model_json_schema()
    properties = schema["properties"]

    assert schema["required"] == ["app_id", "prompt"]
    assert properties["prompt"]["maxLength"] == 600
    assert properties["mode"]["default"] == "full"
    assert properties["target_polycount"] == {
        "default": 30_000,
        "description": (
            "Target number of polygons in the generated model. When model_type is "
            "'smart-topology' and this is left unset, Meshy's lower smart-topology "
            "default (4,000) is used instead; smart topology accepts at most 15,000."
        ),
        "maximum": 300_000,
        "minimum": 100,
        "title": "Target Polycount",
        "type": "integer",
    }
    assert properties["rigging_height_meters"]["exclusiveMinimum"] == 0
    assert properties["is_a_t_pose"]["deprecated"] is True


@pytest.mark.parametrize("mode", ["preview", "full"])
def test_meshy_v7_text_to_3d_accepts_mode_enum(mode: str) -> None:
    config = MeshyV7TextTo3dConfig(app_id=APP_ID, prompt="A chair.", mode=mode)

    assert config.mode == mode


@pytest.mark.parametrize("model_type", ["standard", "lowpoly", "smart-topology"])
def test_meshy_v7_text_to_3d_accepts_model_type_enum(model_type: str) -> None:
    config = MeshyV7TextTo3dConfig(
        app_id=APP_ID,
        prompt="A chair.",
        model_type=model_type,
    )

    assert config.model_type == model_type


@pytest.mark.parametrize("topology", ["quad", "triangle"])
def test_meshy_v7_text_to_3d_accepts_topology_enum(topology: str) -> None:
    config = MeshyV7TextTo3dConfig(
        app_id=APP_ID,
        prompt="A chair.",
        topology=topology,
    )

    assert config.topology == topology


@pytest.mark.parametrize("symmetry_mode", ["off", "auto", "on"])
def test_meshy_v7_text_to_3d_accepts_symmetry_mode_enum(symmetry_mode: str) -> None:
    config = MeshyV7TextTo3dConfig(
        app_id=APP_ID,
        prompt="A chair.",
        symmetry_mode=symmetry_mode,
    )

    assert config.symmetry_mode == symmetry_mode


@pytest.mark.parametrize("pose_mode", ["a-pose", "t-pose", ""])
def test_meshy_v7_text_to_3d_accepts_pose_mode_enum(pose_mode: str) -> None:
    config = MeshyV7TextTo3dConfig(
        app_id=APP_ID,
        prompt="A character.",
        pose_mode=pose_mode,
    )

    assert config.pose_mode == pose_mode


def test_meshy_v7_text_to_3d_accepts_nullable_openapi_fields() -> None:
    config = MeshyV7TextTo3dConfig(
        app_id=APP_ID,
        prompt="A chair.",
        seed=None,
        texture_prompt=None,
        texture_image_url=None,
    )

    assert config.seed is None
    assert config.texture_prompt is None
    assert config.texture_image_url is None


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID}, "prompt"),
        ({"app_id": APP_ID, "prompt": "p" * 601}, "prompt"),
        ({"app_id": APP_ID, "prompt": "A chair.", "mode": "draft"}, "mode"),
        ({"app_id": APP_ID, "prompt": "A chair.", "model_type": "highpoly"}, "model_type"),
        ({"app_id": APP_ID, "prompt": "A chair.", "topology": "ngon"}, "topology"),
        ({"app_id": APP_ID, "prompt": "A chair.", "symmetry_mode": "mirror"}, "symmetry_mode"),
        ({"app_id": APP_ID, "prompt": "A chair.", "pose_mode": "standing"}, "pose_mode"),
        ({"app_id": APP_ID, "prompt": "A chair.", "target_polycount": 99}, "target_polycount"),
        (
            {"app_id": APP_ID, "prompt": "A chair.", "target_polycount": 300_001},
            "target_polycount",
        ),
        (
            {"app_id": APP_ID, "prompt": "A chair.", "rigging_height_meters": 0},
            "rigging_height_meters",
        ),
        ({"app_id": APP_ID, "prompt": "A chair.", "texture_prompt": "t" * 601}, "texture_prompt"),
        ({"app_id": APP_ID, "prompt": "A chair.", "topology": None}, "topology"),
        ({"app_id": APP_ID, "prompt": "A chair.", "unexpected": True}, "unexpected"),
    ],
)
def test_meshy_v7_text_to_3d_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MeshyV7TextTo3dConfig.model_validate(payload)
