from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import Vggt1bConfig

APP_ID = "fal-ai/vggt-1b"


def test_vggt_1b_accepts_no_parameter_fields_as_openapi_allows() -> None:
    config = Vggt1bConfig(app_id=APP_ID)

    assert config.model_dump() == {
        "app_id": APP_ID,
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
    }


def test_vggt_1b_accepts_all_fields_at_boundaries() -> None:
    config = Vggt1bConfig(
        app_id=APP_ID,
        image_urls=[f"https://example.com/view-{index}.png" for index in range(48)],
        video_url="https://example.com/orbit.mp4",
        frame_sampling_rate=1_000,
        alpha_blend_onto="mean",
        export_prediction_data=False,
        export_depth_maps=False,
        export_point_cloud=False,
        array_encoding="list",
        exclude_keys=[
            "image",
            "pose_enc",
            "extrinsic",
            "intrinsic",
            "depth",
            "depth_conf",
            "mask",
            "original_image",
        ],
        confidence_percentile=100,
        max_points=5_000_000,
        enable_safety_checker=False,
    )

    assert len(config.image_urls) == 48
    assert config.video_url == "https://example.com/orbit.mp4"
    assert config.exclude_keys[-1] == "original_image"
    assert config.confidence_percentile == 100
    assert config.max_points == 5_000_000


def test_vggt_1b_preserves_required_defaults_and_bounds_in_schema() -> None:
    schema = Vggt1bConfig.model_json_schema()
    properties = schema["properties"]

    assert schema["required"] == ["app_id"]
    assert properties["image_urls"]["maxItems"] == 48
    assert "default" not in properties["image_urls"]
    assert "default" not in properties["exclude_keys"]
    assert properties["frame_sampling_rate"]["minimum"] == 1
    assert properties["frame_sampling_rate"]["maximum"] == 1_000
    assert properties["confidence_percentile"]["minimum"] == 0
    assert properties["confidence_percentile"]["maximum"] == 100
    assert properties["max_points"]["minimum"] == 1_000
    assert properties["max_points"]["maximum"] == 5_000_000


@pytest.mark.parametrize("array_encoding", ["base64", "list"])
def test_vggt_1b_accepts_array_encoding_enum(array_encoding: str) -> None:
    config = Vggt1bConfig(app_id=APP_ID, array_encoding=array_encoding)

    assert config.array_encoding == array_encoding


@pytest.mark.parametrize("alpha_blend_onto", ["keep", "white", "black", "mean"])
def test_vggt_1b_accepts_alpha_blend_enum(alpha_blend_onto: str) -> None:
    config = Vggt1bConfig(app_id=APP_ID, alpha_blend_onto=alpha_blend_onto)

    assert config.alpha_blend_onto == alpha_blend_onto


def test_vggt_1b_accepts_explicit_null_video_url() -> None:
    config = Vggt1bConfig(app_id=APP_ID, video_url=None)

    assert config.video_url is None


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "image_urls": None}, "image_urls"),
        ({"app_id": APP_ID, "exclude_keys": None}, "exclude_keys"),
        (
            {
                "app_id": APP_ID,
                "image_urls": [
                    f"https://example.com/view-{index}.png" for index in range(49)
                ],
            },
            "image_urls",
        ),
        ({"app_id": APP_ID, "frame_sampling_rate": 0}, "frame_sampling_rate"),
        ({"app_id": APP_ID, "frame_sampling_rate": 1_001}, "frame_sampling_rate"),
        ({"app_id": APP_ID, "array_encoding": "json"}, "array_encoding"),
        ({"app_id": APP_ID, "alpha_blend_onto": "transparent"}, "alpha_blend_onto"),
        ({"app_id": APP_ID, "exclude_keys": ["timings"]}, "exclude_keys"),
        ({"app_id": APP_ID, "confidence_percentile": -0.1}, "confidence_percentile"),
        ({"app_id": APP_ID, "confidence_percentile": 100.1}, "confidence_percentile"),
        ({"app_id": APP_ID, "max_points": 999}, "max_points"),
        ({"app_id": APP_ID, "max_points": 5_000_001}, "max_points"),
        ({"app_id": APP_ID, "unexpected": True}, "unexpected"),
    ],
)
def test_vggt_1b_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Vggt1bConfig.model_validate(payload)
