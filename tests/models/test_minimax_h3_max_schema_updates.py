"""Validate MiniMax H3 Max, H3 Max Turbo, and Music 3 inputs against the current API."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import validate_parameters

VIDEO_IDS = [
    "minimax/h3-max-turbo/image-to-video",
    "minimax/h3-max-turbo/text-to-video",
    "minimax/h3-max/image-to-video",
    "minimax/h3-max/reference-to-video",
    "minimax/h3-max/text-to-video",
]
CAMERA_ID = "minimax/h3-max/camera-controls"
REFERENCE_ID = "minimax/h3-max/reference-to-video"
PARAMETERS = {"prompt": "A quiet garden.", "prompt_expansion_mode": "balanced"}
CAMERA_PARAMETERS = {
    "image_url": "https://example.com/start.png",
    "prompt_expansion_mode": "balanced",
}


@pytest.mark.parametrize("app_id", [*VIDEO_IDS, CAMERA_ID, "minimax/music-3"])
def test_schema_example_parameters_pass_validation(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    config = validate_parameters(payload["app_id"], payload["parameters"])

    assert config is not None
    assert config.app_id == app_id
    assert all(
        config.model_dump()[field] == value for field, value in payload["parameters"].items()
    )


@pytest.mark.parametrize("app_id", VIDEO_IDS)
@pytest.mark.parametrize(
    "url", [None, "https://example.com/audio.wav", "data:audio/wav;base64,YQ=="]
)
def test_video_preserves_optional_target_audio(app_id: str, url: str | None) -> None:
    config = validate_parameters(app_id, {**PARAMETERS, "target_audio_url": url})

    assert config.model_dump()["target_audio_url"] == url


@pytest.mark.parametrize("app_id", VIDEO_IDS)
@pytest.mark.parametrize("url", ["", " \t\n"])
def test_video_rejects_empty_target_audio(app_id: str, url: str) -> None:
    with pytest.raises(ValidationError, match="target_audio_url"):
        validate_parameters(app_id, {**PARAMETERS, "target_audio_url": url})


@pytest.mark.parametrize("app_id", VIDEO_IDS)
def test_video_requires_two_seconds_with_target_audio(app_id: str) -> None:
    parameters = {**PARAMETERS, "target_audio_url": "https://example.com/audio.wav"}
    with pytest.raises(ValidationError, match="duration"):
        validate_parameters(app_id, {**parameters, "duration": 1.99})

    assert validate_parameters(app_id, {**parameters, "duration": 2}).duration == 2


def _poses(count: int = 2) -> dict[str, object]:
    matrix = [[1.0 if row == col else 0.0 for col in range(4)] for row in range(4)]
    return {"convention": "blender", "c2w": [matrix for _ in range(count)]}


@pytest.mark.parametrize("convention", ["blender", "opencv"])
@pytest.mark.parametrize("count", [2, 2048])
def test_camera_preserves_imported_matrices(convention: str, count: int) -> None:
    poses = {**_poses(count), "convention": convention}
    config = validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "camera_poses": poses})

    assert config.model_dump()["camera_poses"] == poses


@pytest.mark.parametrize(
    "poses",
    [
        {"convention": "other", "c2w": _poses()["c2w"]},
        {"c2w": _poses()["c2w"]},
        {"convention": "blender"},
        _poses(1),
        _poses(2049),
        {"convention": "blender", "c2w": [[[0] * 4] * 3] * 2},
        {"convention": "blender", "c2w": [[[0] * 3] * 4] * 2},
        {"convention": "blender", "c2w": [[[0] * 4] * 5] * 2},
        {"convention": "blender", "c2w": [[[0] * 5] * 4] * 2},
    ],
)
def test_camera_checks_imported_pose_shape(poses: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="camera_poses"):
        validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "camera_poses": poses})


@pytest.mark.parametrize("scale", [0.001, 10000])
def test_camera_accepts_translation_scale_boundaries(scale: float) -> None:
    config = validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "camera_poses_scale": scale})

    assert config.model_dump()["camera_poses_scale"] == scale


@pytest.mark.parametrize("scale", [0, -0.01, 10000.01])
def test_camera_rejects_invalid_translation_scale(scale: float) -> None:
    with pytest.raises(ValidationError, match="camera_poses_scale"):
        validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "camera_poses_scale": scale})


@pytest.mark.parametrize(
    "preset",
    [
        None,
        "truck_right",
        "truck_left",
        "pedestal_up",
        "pedestal_down",
        "dolly_in",
        "dolly_out",
        "pan_right",
        "pan_left",
        "tilt_up",
        "tilt_down",
        "roll_right",
        "roll_left",
        "s_curve_forward",
    ],
)
def test_camera_preserves_free_camera_preset(preset: str | None) -> None:
    config = validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "free_camera_preset": preset})

    assert config.model_dump()["free_camera_preset"] == preset


def test_camera_rejects_unknown_preset() -> None:
    with pytest.raises(ValidationError, match="free_camera_preset"):
        validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "free_camera_preset": "orbit"})


def test_camera_accepts_null_trajectory() -> None:
    config = validate_parameters(CAMERA_ID, {**CAMERA_PARAMETERS, "camera_trajectory": None})

    assert config.model_dump()["camera_trajectory"] is None


def test_reference_video_preserves_reference_order_and_limit() -> None:
    references = [
        {"type": "audio", "url": "https://example.com/audio.wav"},
        {"type": "image", "url": "https://example.com/image.png"},
        {"type": "video", "url": "https://example.com/video.mp4"},
    ] * 4
    config = validate_parameters(REFERENCE_ID, {**PARAMETERS, "reference_conditions": references})

    assert config.model_dump()["reference_conditions"] == references
    with pytest.raises(ValidationError, match="reference_conditions"):
        validate_parameters(
            REFERENCE_ID, {**PARAMETERS, "reference_conditions": references + references[:1]}
        )


@pytest.mark.parametrize(
    "reference",
    [
        {"type": "image"},
        {"url": "https://example.com/image.png"},
        {"type": "text", "url": "https://example.com/text"},
        {"type": "image", "url": ""},
    ],
)
def test_reference_video_checks_ordered_reference_fields(reference: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        validate_parameters(REFERENCE_ID, {**PARAMETERS, "reference_conditions": [reference]})


@pytest.mark.parametrize(
    "field", ["reference_image_urls", "reference_video_urls", "reference_audio_urls"]
)
def test_reference_video_rejects_mixed_reference_forms(field: str) -> None:
    with pytest.raises(ValidationError, match="reference_conditions"):
        validate_parameters(
            REFERENCE_ID,
            {
                **PARAMETERS,
                "reference_conditions": [{"type": "image", "url": "https://example.com/ref"}],
                field: ["https://example.com/ref"],
            },
        )


@pytest.mark.parametrize("ordered", [False, True])
def test_reference_video_rejects_reference_audio_with_target_audio(ordered: bool) -> None:
    references = (
        {"reference_conditions": [{"type": "audio", "url": "https://example.com/ref.wav"}]}
        if ordered
        else {"reference_audio_urls": ["https://example.com/ref.wav"]}
    )
    with pytest.raises(ValidationError, match="target_audio_url"):
        validate_parameters(
            REFERENCE_ID,
            {**PARAMETERS, **references, "target_audio_url": "https://example.com/target.wav"},
        )


@pytest.mark.parametrize("resolution", ["480P", "768P"])
@pytest.mark.parametrize("time", [None, 0.001, 2.5, 14.999])
def test_reference_video_preserves_middle_keyframe(resolution: str, time: float | None) -> None:
    parameters = {
        **PARAMETERS,
        "image_url": "https://example.com/start.png",
        "end_image_url": "https://example.com/end.png",
        "middle_image_url": "https://example.com/middle.png",
        "middle_frame_time": time,
        "resolution": resolution,
    }
    config = validate_parameters(REFERENCE_ID, parameters)

    assert config.model_dump().items() >= parameters.items()


@pytest.mark.parametrize("field", ["image_url", "end_image_url", "middle_image_url"])
def test_reference_video_rejects_empty_keyframe_url(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(REFERENCE_ID, {**PARAMETERS, field: ""})


@pytest.mark.parametrize("time", [0, -0.001, 15, 15.001])
def test_reference_video_checks_middle_time_boundaries(time: float) -> None:
    with pytest.raises(ValidationError, match="middle_frame_time"):
        validate_parameters(
            REFERENCE_ID,
            {
                **PARAMETERS,
                "image_url": "https://example.com/start.png",
                "end_image_url": "https://example.com/end.png",
                "middle_image_url": "https://example.com/middle.png",
                "middle_frame_time": time,
            },
        )


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"middle_frame_time": 2.5}, "middle_frame_time"),
        ({"middle_image_url": "https://example.com/middle.png"}, "middle_image_url"),
        (
            {
                "middle_image_url": "https://example.com/middle.png",
                "image_url": "https://example.com/start.png",
            },
            "middle_image_url",
        ),
        (
            {
                "middle_image_url": "https://example.com/middle.png",
                "end_image_url": "https://example.com/end.png",
            },
            "middle_image_url",
        ),
        (
            {
                "middle_image_url": "https://example.com/middle.png",
                "image_url": "https://example.com/start.png",
                "end_image_url": "https://example.com/end.png",
                "resolution": "1080P",
            },
            "middle_image_url",
        ),
    ],
)
def test_reference_video_checks_middle_keyframe_dependencies(
    parameters: dict[str, object], needle: str
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate_parameters(REFERENCE_ID, {**PARAMETERS, **parameters})


@pytest.mark.parametrize("enabled", [True, False])
def test_music_preserves_safety_checker_setting(enabled: bool) -> None:
    config = validate_parameters(
        "minimax/music-3", {"prompt": "Ambient.", "lyrics": "", "enable_safety_checker": enabled}
    )

    assert config.model_dump()["enable_safety_checker"] is enabled
