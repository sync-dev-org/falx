from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    Flux3ExtendVideoConfig,
    Flux3FirstLastFrameToVideoConfig,
    Flux3ImageToVideoConfig,
    Flux3Keyframe,
    Flux3KeyframesToVideoConfig,
    Flux3TextToVideoConfig,
    config_class_for_app_id,
)


def test_flux_3_text_to_video_accepts_schema_defaults() -> None:
    config = Flux3TextToVideoConfig(
        app_id="blackforestlabs/flux-3/text-to-video",
        prompt="A red panda walks along a mossy log in a sunlit forest.",
    )

    assert config.model_dump() == {
        "prompt": "A red panda walks along a mossy log in a sunlit forest.",
        "resolution": "720p",
        "safety_tolerance": 2,
        "generate_audio": True,
        "aspect_ratio": "auto",
        "app_id": "blackforestlabs/flux-3/text-to-video",
        "duration": "auto",
    }


def test_flux_3_image_to_video_accepts_schema_defaults() -> None:
    config = Flux3ImageToVideoConfig(
        app_id="blackforestlabs/flux-3/image-to-video",
        prompt="The camera circles the subject in one continuous shot.",
        image_url="https://example.com/start.webp",
    )

    assert config.image_url == "https://example.com/start.webp"
    assert config.resolution == "720p"
    assert config.safety_tolerance == 2
    assert config.generate_audio is True
    assert config.aspect_ratio == "auto"
    assert config.duration == "auto"


def test_flux_3_extend_video_accepts_schema_defaults() -> None:
    config = Flux3ExtendVideoConfig(
        app_id="blackforestlabs/flux-3/extend-video",
        prompt="Continue the forward camera movement into the valley.",
        video_url="https://example.com/source.mp4",
    )

    assert config.video_url == "https://example.com/source.mp4"
    assert config.duration == "auto"
    assert config.generate_audio is True


def test_flux_3_extend_video_schema_preserves_source_constraints() -> None:
    description = Flux3ExtendVideoConfig.model_json_schema()["properties"]["video_url"][
        "description"
    ]

    assert "MP4" in description
    assert "50 MB" in description
    assert "15 seconds" in description


def test_flux_3_extend_video_schema_preserves_route_specific_prompt_contract() -> None:
    description = Flux3ExtendVideoConfig.model_json_schema()["properties"]["prompt"][
        "description"
    ]

    assert description == (
        "The text prompt describing how the video continues from the source clip's final frames."
    )


def test_flux_3_first_last_frame_to_video_accepts_schema_defaults() -> None:
    config = Flux3FirstLastFrameToVideoConfig(
        app_id="blackforestlabs/flux-3/first-last-frame-to-video",
        prompt="Move smoothly from sunrise to sunset.",
        start_image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
    )

    assert config.duration == 5
    assert config.start_image_url == "https://example.com/start.png"
    assert config.end_image_url == "https://example.com/end.png"


def test_flux_3_keyframes_to_video_accepts_schema_defaults() -> None:
    config = Flux3KeyframesToVideoConfig(
        app_id="blackforestlabs/flux-3/keyframes-to-video",
        prompt="Interpolate one continuous camera move between the anchors.",
        keyframes=[
            {"image_url": "https://example.com/start.png", "frame_index": 0},
            {"image_url": "https://example.com/end.png", "frame_index": 120},
        ],
    )

    assert config.duration == 5
    assert config.keyframes == [
        Flux3Keyframe(image_url="https://example.com/start.png", frame_index=0),
        Flux3Keyframe(image_url="https://example.com/end.png", frame_index=120),
    ]


def test_flux_3_keyframes_schema_exposes_openapi_bounds() -> None:
    schema = Flux3KeyframesToVideoConfig.model_json_schema()

    assert schema["properties"]["keyframes"]["minItems"] == 1
    assert schema["properties"]["keyframes"]["maxItems"] == 10
    assert schema["$defs"]["Flux3Keyframe"]["properties"]["frame_index"]["minimum"] == 0


@pytest.mark.parametrize("resolution", ["720p", "1080p"])
def test_flux_3_accepts_resolution_enum(resolution: str) -> None:
    config = Flux3TextToVideoConfig.model_validate(
        {
            "app_id": "blackforestlabs/flux-3/text-to-video",
            "prompt": "A cinematic landscape.",
            "resolution": resolution,
        }
    )

    assert config.resolution == resolution


@pytest.mark.parametrize(
    "aspect_ratio",
    ["auto", "21:9", "2:1", "16:9", "4:3", "1:1", "3:4", "9:16"],
)
def test_flux_3_accepts_aspect_ratio_enum(aspect_ratio: str) -> None:
    config = Flux3TextToVideoConfig.model_validate(
        {
            "app_id": "blackforestlabs/flux-3/text-to-video",
            "prompt": "A cinematic landscape.",
            "aspect_ratio": aspect_ratio,
        }
    )

    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("duration", ["auto", *range(5, 21)])
def test_flux_3_flexible_routes_accept_duration_enum(duration: str | int) -> None:
    config = Flux3TextToVideoConfig.model_validate(
        {
            "app_id": "blackforestlabs/flux-3/text-to-video",
            "prompt": "A cinematic landscape.",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize("duration", range(5, 21))
def test_flux_3_fixed_duration_routes_accept_duration_enum(duration: int) -> None:
    config = Flux3FirstLastFrameToVideoConfig.model_validate(
        {
            "app_id": "blackforestlabs/flux-3/first-last-frame-to-video",
            "prompt": "A cinematic transition.",
            "start_image_url": "https://example.com/start.png",
            "end_image_url": "https://example.com/end.png",
            "duration": duration,
        }
    )

    assert config.duration == duration


@pytest.mark.parametrize("safety_tolerance", range(5))
def test_flux_3_accepts_safety_tolerance_bounds(safety_tolerance: int) -> None:
    config = Flux3TextToVideoConfig(
        app_id="blackforestlabs/flux-3/text-to-video",
        prompt="A cinematic landscape.",
        safety_tolerance=safety_tolerance,
    )

    assert config.safety_tolerance == safety_tolerance


@pytest.mark.parametrize(
    ("config_class", "payload", "needle"),
    [
        (
            Flux3TextToVideoConfig,
            {"app_id": "blackforestlabs/flux-3/text-to-video"},
            "prompt",
        ),
        (
            Flux3ImageToVideoConfig,
            {
                "app_id": "blackforestlabs/flux-3/image-to-video",
                "prompt": "Animate the image.",
            },
            "image_url",
        ),
        (
            Flux3ExtendVideoConfig,
            {
                "app_id": "blackforestlabs/flux-3/extend-video",
                "prompt": "Continue the video.",
            },
            "video_url",
        ),
        (
            Flux3FirstLastFrameToVideoConfig,
            {
                "app_id": "blackforestlabs/flux-3/first-last-frame-to-video",
                "prompt": "Transition between frames.",
                "end_image_url": "https://example.com/end.png",
            },
            "start_image_url",
        ),
        (
            Flux3FirstLastFrameToVideoConfig,
            {
                "app_id": "blackforestlabs/flux-3/first-last-frame-to-video",
                "prompt": "Transition between frames.",
                "start_image_url": "https://example.com/start.png",
            },
            "end_image_url",
        ),
        (
            Flux3KeyframesToVideoConfig,
            {
                "app_id": "blackforestlabs/flux-3/keyframes-to-video",
                "prompt": "Interpolate the anchors.",
            },
            "keyframes",
        ),
    ],
)
def test_flux_3_routes_require_route_specific_inputs(
    config_class: type[Any],
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        config_class.model_validate(payload)


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"resolution": "4k"}, "resolution"),
        ({"aspect_ratio": "3:2"}, "aspect_ratio"),
        ({"duration": 4}, "duration"),
        ({"duration": 21}, "duration"),
        ({"safety_tolerance": -1}, "safety_tolerance"),
        ({"safety_tolerance": 5}, "safety_tolerance"),
        ({"unexpected": True}, "unexpected"),
    ],
)
def test_flux_3_text_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Flux3TextToVideoConfig.model_validate(
            {
                "app_id": "blackforestlabs/flux-3/text-to-video",
                "prompt": "A cinematic landscape.",
                **payload,
            }
        )


@pytest.mark.parametrize(
    ("keyframes", "duration", "needle"),
    [
        ([], 5, "keyframes"),
        (
            [
                {"image_url": f"https://example.com/{index}.png", "frame_index": index}
                for index in range(11)
            ],
            5,
            "keyframes",
        ),
        (
            [
                {"image_url": "https://example.com/a.png", "frame_index": 12},
                {"image_url": "https://example.com/b.png", "frame_index": 12},
            ],
            5,
            "unique",
        ),
        (
            [{"image_url": "https://example.com/a.png", "frame_index": 121}],
            5,
            r"duration \* 24",
        ),
        (
            [{"image_url": "https://example.com/a.png", "frame_index": -1}],
            5,
            "frame_index",
        ),
    ],
)
def test_flux_3_keyframes_reject_invalid_positions(
    keyframes: list[dict[str, object]],
    duration: int,
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Flux3KeyframesToVideoConfig.model_validate(
            {
                "app_id": "blackforestlabs/flux-3/keyframes-to-video",
                "prompt": "Interpolate the anchors.",
                "duration": duration,
                "keyframes": keyframes,
            }
        )


@pytest.mark.parametrize(
    ("app_id", "config_class"),
    [
        ("blackforestlabs/flux-3/text-to-video", Flux3TextToVideoConfig),
        ("blackforestlabs/flux-3/image-to-video", Flux3ImageToVideoConfig),
        ("blackforestlabs/flux-3/extend-video", Flux3ExtendVideoConfig),
        (
            "blackforestlabs/flux-3/first-last-frame-to-video",
            Flux3FirstLastFrameToVideoConfig,
        ),
        ("blackforestlabs/flux-3/keyframes-to-video", Flux3KeyframesToVideoConfig),
    ],
)
def test_flux_3_routes_are_registered(
    app_id: str,
    config_class: type[Any],
) -> None:
    assert app_id in SUPPORTED_APP_IDS
    assert config_class_for_app_id(app_id) is config_class
