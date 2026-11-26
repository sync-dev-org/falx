from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from falx.models import (
    Flux3MaxImageToVideoConfig,
    Flux3MaxKeyframesToVideoConfig,
    Flux3MaxTextToVideoConfig,
)

ROUTES = [
    (Flux3MaxTextToVideoConfig, "text-to-video", {}),
    (Flux3MaxImageToVideoConfig, "image-to-video", {"image_url": "https://example.com/a.png"}),
    (
        Flux3MaxKeyframesToVideoConfig,
        "keyframes-to-video",
        {"keyframes": [{"image_url": "https://example.com/a.png", "frame_index": 0}]},
    ),
]


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_flux_3_max_defaults(config_class: type[Any], route: str, inputs: dict[str, Any]) -> None:
    app_id = f"blackforestlabs/flux-3-max/{route}"
    config = config_class.model_validate({"app_id": app_id, "prompt": "A forest.", **inputs})

    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "A forest.",
        "duration": 5,
        "resolution": "720p",
        "aspect_ratio": "auto",
        "generate_audio": True,
        "reasoning_level": "high",
        "seed": None,
        **({"end_image_url": None} if route == "image-to-video" else {}),
        **inputs,
    }


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        *[("duration", value) for value in range(5, 21)],
        *[("resolution", value) for value in ["720p", "1080p", "2K", "4K"]],
        *[
            ("aspect_ratio", value)
            for value in ["auto", "21:9", "2:1", "16:9", "4:3", "1:1", "3:4", "9:16"]
        ],
        ("reasoning_level", "low"),
        ("generate_audio", False),
        ("seed", 42),
    ],
)
def test_flux_3_max_accepts_options(
    config_class: type[Any], route: str, inputs: dict[str, Any], field: str, value: Any
) -> None:
    config = config_class.model_validate(
        {
            "app_id": f"blackforestlabs/flux-3-max/{route}",
            "prompt": "A forest.",
            **inputs,
            field: value,
        }
    )
    assert getattr(config, field) == value


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", ""),
        ("duration", 4),
        ("duration", 21),
        ("duration", "auto"),
        ("resolution", "4k"),
        ("aspect_ratio", "3:2"),
        ("reasoning_level", "balanced"),
        ("safety_tolerance", 2),
        ("unexpected", True),
    ],
)
def test_flux_3_max_rejects_invalid_options(
    config_class: type[Any], route: str, inputs: dict[str, Any], field: str, value: Any
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_class.model_validate(
            {
                "app_id": f"blackforestlabs/flux-3-max/{route}",
                "prompt": "A forest.",
                **inputs,
                field: value,
            }
        )


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_flux_3_max_requires_prompt_and_route_inputs(
    config_class: type[Any], route: str, inputs: dict[str, Any]
) -> None:
    payload = {"app_id": f"blackforestlabs/flux-3-max/{route}", "prompt": "A forest.", **inputs}
    for field in ["prompt", *inputs]:
        with pytest.raises(ValidationError, match=field):
            config_class.model_validate(
                {key: value for key, value in payload.items() if key != field}
            )


def test_flux_3_max_image_to_video_accepts_last_frame() -> None:
    config = Flux3MaxImageToVideoConfig(
        app_id="blackforestlabs/flux-3-max/image-to-video",
        prompt="Transition to the final frame.",
        image_url="https://example.com/a.png",
        end_image_url="https://example.com/b.png",
    )
    assert config.end_image_url == "https://example.com/b.png"


def test_flux_3_max_keyframes_accepts_ten_unique_frames_at_duration_boundary() -> None:
    frames = [
        {"image_url": f"https://example.com/{index}.png", "frame_index": index * 48}
        for index in range(1, 11)
    ]
    config = Flux3MaxKeyframesToVideoConfig(
        app_id="blackforestlabs/flux-3-max/keyframes-to-video",
        prompt="Move through the anchors.",
        duration=20,
        keyframes=frames,
    )
    assert config.model_dump()["keyframes"] == frames


@pytest.mark.parametrize(
    ("frames", "needle"),
    [
        ([], "keyframes"),
        (
            [{"image_url": "https://example.com/a.png", "frame_index": i} for i in range(11)],
            "keyframes",
        ),
        ([{"image_url": "https://example.com/a.png", "frame_index": 0}] * 2, "unique"),
        ([{"image_url": "https://example.com/a.png", "frame_index": 121}], r"duration \* 24"),
        ([{"image_url": "https://example.com/a.png", "frame_index": -1}], "frame_index"),
        ([{"image_url": "https://example.com/a.png"}], "frame_index"),
        ([{"frame_index": 0}], "image_url"),
        ([{"image_url": "https://example.com/a.png", "frame_index": 0, "extra": 1}], "extra"),
    ],
)
def test_flux_3_max_keyframes_rejects_invalid_anchors(
    frames: list[dict[str, Any]], needle: str
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Flux3MaxKeyframesToVideoConfig(
            app_id="blackforestlabs/flux-3-max/keyframes-to-video",
            prompt="Move through the anchors.",
            keyframes=frames,
        )
