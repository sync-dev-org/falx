from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    Hyper3dLowpolyImageTo3dConfig,
    Hyper3dLowpolyMeshTo3dConfig,
    Hyper3dLowpolyTextTo3dConfig,
)

CASES = [
    (Hyper3dLowpolyImageTo3dConfig, "hyper3d/lowpoly/image-to-3d", {"image_urls": ["image"]}),
    (Hyper3dLowpolyMeshTo3dConfig, "hyper3d/lowpoly/mesh-to-3d", {"model_url": "mesh"}),
    (Hyper3dLowpolyTextTo3dConfig, "hyper3d/lowpoly/text-to-3d", {"prompt": "A robot"}),
]
COMMON_DEFAULTS = {
    "face_count": 4000,
    "geometry_file_format": "glb",
    "rigging": False,
    "rigging_bone_template": "auto",
    "resolution": "Basic",
    "mesh_mode": "Quad",
    "rigging_skinning_method": "shell",
}
TEXTURE_DEFAULTS = {"texture_mode": "medium", "uhd_texture": False, "material": "Shaded"}


@pytest.mark.parametrize(("config_class", "app_id", "parameters"), CASES)
def test_lowpoly_preserves_defaults(config_class, app_id, parameters) -> None:
    extra = {"transfer_texture": True} if app_id.endswith("mesh-to-3d") else TEXTURE_DEFAULTS
    if app_id.endswith("image-to-3d"):
        extra = {**extra, "prompt": "", "image_labels": None}

    config = config_class.model_validate({"app_id": app_id, **parameters})

    assert config.model_dump() == {"app_id": app_id, **COMMON_DEFAULTS, **extra, **parameters}


@pytest.mark.parametrize(("config_class", "app_id", "parameters"), CASES)
@pytest.mark.parametrize("face_count", [200, 10000])
def test_lowpoly_accepts_face_count_boundaries(
    config_class, app_id, parameters, face_count
) -> None:
    config = config_class.model_validate({"app_id": app_id, **parameters, "face_count": face_count})

    assert config.face_count == face_count


@pytest.mark.parametrize(("config_class", "app_id", "parameters"), CASES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        *(("geometry_file_format", v) for v in ["fbx", "glb", "obj", "stl", "usdz"]),
        *(
            ("rigging_bone_template", v)
            for v in ["auto", "human", "quadruped", "bird", "dragon", "kaiju"]
        ),
        *(("resolution", v) for v in ["Basic", "High"]),
        *(("mesh_mode", v) for v in ["Quad", "Raw", "NGon"]),
        *(("rigging_skinning_method", v) for v in ["shell", "core"]),
        ("rigging", True),
    ],
)
def test_lowpoly_accepts_output_and_rigging_options(
    config_class, app_id, parameters, field, value
) -> None:
    config = config_class.model_validate({"app_id": app_id, **parameters, field: value})

    assert config.model_dump()[field] == value


@pytest.mark.parametrize(("config_class", "app_id", "parameters"), [CASES[0], CASES[2]])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        *(
            ("texture_mode", v)
            for v in ["extreme-low", "low", "medium", "high", "extreme-high", "legacy"]
        ),
        *(("material", v) for v in ["PBR", "Shaded", "Hybrid", "All", "None"]),
        ("uhd_texture", True),
        ("prompt", "p" * 1024),
    ],
)
def test_lowpoly_generation_accepts_texture_options_and_prompt_limit(
    config_class, app_id, parameters, field, value
) -> None:
    config = config_class.model_validate({"app_id": app_id, **parameters, field: value})

    assert config.model_dump()[field] == value


@pytest.mark.parametrize(("config_class", "app_id", "parameters"), CASES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("face_count", 199),
        ("face_count", 10001),
        ("geometry_file_format", "ply"),
        ("rigging", None),
        ("rigging_bone_template", "custom"),
        ("resolution", "high"),
        ("mesh_mode", "triangle"),
        ("rigging_skinning_method", "other"),
        ("unexpected", True),
    ],
)
def test_lowpoly_rejects_invalid_common_parameters(
    config_class, app_id, parameters, field, value
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_class.model_validate({"app_id": app_id, **parameters, field: value})


@pytest.mark.parametrize(("config_class", "app_id", "parameters"), CASES)
def test_lowpoly_requires_its_source(config_class, app_id, parameters) -> None:
    with pytest.raises(ValidationError, match=next(iter(parameters))):
        config_class.model_validate({"app_id": app_id})


@pytest.mark.parametrize(
    ("config_class", "app_id", "parameters", "field", "value"),
    [
        (*CASES[0], "image_urls", []),
        (*CASES[0], "image_urls", ["image"] * 6),
        (*CASES[0], "image_urls", [None]),
        (*CASES[0], "image_labels", ["F"] * 6),
        (*CASES[0], "image_labels", ["front"]),
        (*CASES[0], "prompt", "p" * 1025),
        (*CASES[0], "texture_mode", "ultra"),
        (*CASES[0], "material", "none"),
        (*CASES[1], "model_url", ""),
        (*CASES[1], "transfer_texture", None),
        (*CASES[1], "texture_mode", "medium"),
        (*CASES[2], "prompt", ""),
        (*CASES[2], "prompt", " \t\n"),
        (*CASES[2], "prompt", "p" * 1025),
        (*CASES[2], "texture_mode", "ultra"),
        (*CASES[2], "material", "none"),
    ],
)
def test_lowpoly_rejects_invalid_sources_and_texture_options(
    config_class, app_id, parameters, field, value
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_class.model_validate({"app_id": app_id, **parameters, field: value})


@pytest.mark.parametrize("label", ["F", "FL", "FR", "B", "BL", "BR", "L", "R", "U", "D", "?"])
def test_lowpoly_images_accepts_view_labels(label) -> None:
    config = Hyper3dLowpolyImageTo3dConfig(
        app_id=CASES[0][1], image_urls=["image"] * 5, image_labels=[label] * 5
    )

    assert config.image_labels == [label] * 5


def test_lowpoly_images_allows_empty_labels_and_blank_optional_prompt() -> None:
    config = Hyper3dLowpolyImageTo3dConfig(
        app_id=CASES[0][1], image_urls=["image"], image_labels=[], prompt=""
    )

    assert config.image_labels == []
    assert config.prompt == ""
