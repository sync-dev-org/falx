from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    LumaRay32EditControls,
    LumaRay32EditDepthControl,
    LumaRay32EditFaceControl,
    LumaRay32EditNormalsControl,
    LumaRay32EditPoseControl,
    LumaRay32EditTrajectoryControl,
    LumaRay32ImageToVideoConfig,
    LumaRay32ReframeConfig,
    LumaRay32ReframeSourcePosition,
    LumaRay32TextToVideoConfig,
    LumaRay32VideoToVideoConfig,
)


def test_luma_ray_3_2_text_to_video_accepts_schema_defaults() -> None:
    config = LumaRay32TextToVideoConfig(
        app_id="luma/agent/ray/v3.2/text-to-video",
        prompt="A herd of wild horses galloping across a dusty desert plain.",
    )

    assert config.model_dump() == {
        "app_id": "luma/agent/ray/v3.2/text-to-video",
        "prompt": "A herd of wild horses galloping across a dusty desert plain.",
        "aspect_ratio": "16:9",
        "resolution": "540p",
        "duration": "5s",
        "loop": False,
        "hdr": False,
        "exr_export": False,
        "reference_image_urls": None,
    }


def test_luma_ray_3_2_text_to_video_accepts_all_fields() -> None:
    config = LumaRay32TextToVideoConfig(
        app_id="luma/agent/ray/v3.2/text-to-video",
        prompt="A macro shot of frost spreading over glass.",
        aspect_ratio="21:9",
        resolution="1080p",
        duration="5s",
        hdr=True,
        exr_export=True,
        reference_image_urls=[
            "https://example.com/ref-1.png",
            "https://example.com/ref-2.png",
            "https://example.com/ref-3.png",
            "https://example.com/ref-4.png",
        ],
    )

    assert config.hdr is True
    assert config.exr_export is True
    assert len(config.reference_image_urls or []) == 4


def test_luma_ray_3_2_image_to_video_accepts_first_frame_defaults() -> None:
    config = LumaRay32ImageToVideoConfig(
        app_id="luma/agent/ray/v3.2/image-to-video",
        prompt="A majestic tiger prowls through a snowy landscape.",
        image_url="https://example.com/start.png",
    )

    assert config.model_dump() == {
        "app_id": "luma/agent/ray/v3.2/image-to-video",
        "prompt": "A majestic tiger prowls through a snowy landscape.",
        "image_url": "https://example.com/start.png",
        "end_image_url": None,
        "aspect_ratio": "16:9",
        "resolution": "540p",
        "duration": "5s",
        "loop": False,
        "hdr": False,
        "exr_export": False,
        "reference_image_urls": None,
        "keyframes": None,
        "keyframe_indexes": None,
    }


def test_luma_ray_3_2_image_to_video_accepts_multi_keyframes() -> None:
    config = LumaRay32ImageToVideoConfig(
        app_id="luma/agent/ray/v3.2/image-to-video",
        prompt="Interpolate a precise product turntable.",
        duration="10s",
        resolution="720p",
        hdr=True,
        keyframes=[
            "https://example.com/frame-0.png",
            "https://example.com/frame-120.png",
            "https://example.com/frame-240.png",
        ],
        keyframe_indexes=[0, 120, 240],
    )

    assert config.image_url is None
    assert config.duration == "10s"
    assert config.keyframe_indexes == [0, 120, 240]


def test_luma_ray_3_2_video_to_video_accepts_controls() -> None:
    config = LumaRay32VideoToVideoConfig(
        app_id="luma/agent/ray/v3.2/video-to-video",
        prompt="Restyle the footage as hand-painted watercolor animation.",
        video_url="https://example.com/source.mp4",
        resolution="720p",
        hdr=True,
        controls=LumaRay32EditControls(
            pose=LumaRay32EditPoseControl(strength="precise"),
            depth=LumaRay32EditDepthControl(blur=0.25),
            normals=LumaRay32EditNormalsControl(augmentation=0.3),
            trajectory=LumaRay32EditTrajectoryControl(sparsity=0.6),
            face=LumaRay32EditFaceControl(enabled=False),
        ),
    )

    assert config.model_dump()["controls"] == {
        "pose": {"enabled": True, "strength": "precise"},
        "depth": {"enabled": True, "blur": 0.25},
        "normals": {"enabled": True, "augmentation": 0.3},
        "trajectory": {"enabled": True, "sparsity": 0.6},
        "face": {"enabled": False},
    }


def test_luma_ray_3_2_reframe_accepts_source_position() -> None:
    config = LumaRay32ReframeConfig(
        app_id="luma/agent/ray/v3.2/reframe",
        prompt="Extend the scene into cinematic widescreen.",
        video_url="https://example.com/source.mp4",
        aspect_ratio="21:9",
        source_position=LumaRay32ReframeSourcePosition(
            x_norm=-0.1,
            y_norm=0.0,
            w_norm=1.2,
            h_norm=1.0,
        ),
    )

    assert config.model_dump() == {
        "app_id": "luma/agent/ray/v3.2/reframe",
        "prompt": "Extend the scene into cinematic widescreen.",
        "video_url": "https://example.com/source.mp4",
        "aspect_ratio": "21:9",
        "resolution": "540p",
        "source_position": {
            "x_norm": -0.1,
            "y_norm": 0.0,
            "w_norm": 1.2,
            "h_norm": 1.0,
        },
    }


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": "luma/agent/ray/v3.2/text-to-video"}, "prompt"),
        (
            {
                "app_id": "luma/agent/ray/v3.2/text-to-video",
                "prompt": "A quiet city park.",
                "resolution": "4k",
            },
            "resolution",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/text-to-video",
                "prompt": "A quiet city park.",
                "resolution": "540p",
                "hdr": True,
            },
            "hdr requires resolution",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/text-to-video",
                "prompt": "A quiet city park.",
                "duration": "10s",
                "loop": True,
            },
            "loop requires 5s",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/text-to-video",
                "prompt": "A quiet city park.",
                "loop": True,
                "hdr": True,
            },
            "loop cannot be combined with hdr",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/text-to-video",
                "prompt": "A quiet city park.",
                "exr_export": True,
            },
            "exr_export requires hdr",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/text-to-video",
                "prompt": "A quiet city park.",
                "reference_image_urls": [
                    "https://example.com/1.png",
                    "https://example.com/2.png",
                    "https://example.com/3.png",
                    "https://example.com/4.png",
                    "https://example.com/5.png",
                ],
            },
            "reference_image_urls",
        ),
    ],
)
def test_luma_ray_3_2_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        LumaRay32TextToVideoConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
            },
            "image_url or keyframes",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "end_image_url": "https://example.com/end.png",
            },
            "end_image_url requires image_url",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "image_url": "https://example.com/start.png",
                "keyframes": ["https://example.com/frame.png"],
                "keyframe_indexes": [0],
            },
            "image_url/end_image_url cannot be combined with keyframes",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "image_url": "https://example.com/start.png",
                "duration": "10s",
            },
            "10s requires keyframes",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "keyframes": ["https://example.com/frame.png"],
            },
            "keyframes and keyframe_indexes",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "keyframes": [
                    "https://example.com/frame-0.png",
                    "https://example.com/frame-1.png",
                ],
                "keyframe_indexes": [0],
            },
            "same length",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "keyframes": [
                    "https://example.com/frame-0.png",
                    "https://example.com/frame-1.png",
                ],
                "keyframe_indexes": [0, 0],
            },
            "unique",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "keyframes": ["https://example.com/frame.png"],
                "keyframe_indexes": [-1],
            },
            "non-negative",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/image-to-video",
                "prompt": "Animate the frame.",
                "image_url": "https://example.com/start.png",
                "loop": True,
                "end_image_url": "https://example.com/end.png",
            },
            "loop cannot be combined with end_image_url",
        ),
    ],
)
def test_luma_ray_3_2_image_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        LumaRay32ImageToVideoConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "luma/agent/ray/v3.2/video-to-video",
                "prompt": "Restyle the clip.",
            },
            "video_url",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/video-to-video",
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/source.mp4",
                "resolution": "540p",
                "hdr": True,
            },
            "hdr requires resolution",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/video-to-video",
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/source.mp4",
                "exr_export": True,
            },
            "exr_export requires hdr",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/video-to-video",
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/source.mp4",
                "edit_strength": "flex_2",
                "auto_controls": True,
            },
            "edit_strength cannot be combined with auto_controls",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/video-to-video",
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/source.mp4",
                "auto_controls": True,
                "controls": {"pose": {"strength": "coarse"}},
            },
            "controls cannot be combined with auto_controls",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/video-to-video",
                "prompt": "Restyle the clip.",
                "video_url": "https://example.com/source.mp4",
                "start_image_url": "https://example.com/start.png",
                "keyframes": ["https://example.com/frame.png"],
                "keyframe_indexes": [0],
            },
            "start_image_url cannot be combined with keyframes",
        ),
    ],
)
def test_luma_ray_3_2_video_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        LumaRay32VideoToVideoConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "luma/agent/ray/v3.2/reframe",
                "prompt": "Extend the scene.",
                "video_url": "https://example.com/source.mp4",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/reframe",
                "prompt": "Extend the scene.",
                "video_url": "https://example.com/source.mp4",
                "aspect_ratio": "2:1",
            },
            "aspect_ratio",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/reframe",
                "prompt": "Extend the scene.",
                "video_url": "https://example.com/source.mp4",
                "aspect_ratio": "21:9",
                "source_position": {
                    "x_norm": 0,
                    "y_norm": 0,
                    "w_norm": 0,
                    "h_norm": 1,
                },
            },
            "w_norm",
        ),
        (
            {
                "app_id": "luma/agent/ray/v3.2/reframe",
                "prompt": "Extend the scene.",
                "video_url": "https://example.com/source.mp4",
                "aspect_ratio": "21:9",
                "source_position": {
                    "x_norm": -2.1,
                    "y_norm": 0,
                    "w_norm": 1,
                    "h_norm": 1,
                },
            },
            "x_norm",
        ),
    ],
)
def test_luma_ray_3_2_reframe_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        LumaRay32ReframeConfig.model_validate(payload)
