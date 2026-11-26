from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from falx.models import (
    GrokImagineVideoV15LiteImageToVideoConfig,
    GrokImagineVideoV15LiteTextToVideoConfig,
)

ROUTES = [
    (GrokImagineVideoV15LiteTextToVideoConfig, "text-to-video", {}),
    (
        GrokImagineVideoV15LiteImageToVideoConfig,
        "image-to-video",
        {"image_url": "https://example.com/a.png"},
    ),
]


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_grok_lite_defaults(config_class: type[Any], route: str, inputs: dict[str, Any]) -> None:
    app_id = f"xai/grok-imagine-video/v1.5/lite/{route}"
    config = config_class.model_validate({"app_id": app_id, "prompt": "A forest.", **inputs})
    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "A forest.",
        "duration": 6,
        "resolution": "720p",
        "generate_audio": None,
        "enable_safety_checker": True,
        **(
            {"aspect_ratio": "16:9"}
            if route == "text-to-video"
            else {
                "end_image_url": None,
                "keyframes": None,
            }
        ),
        **inputs,
    }


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 1),
        ("duration", 15),
        ("prompt", ""),
        ("prompt", "x" * 4096),
        *[("resolution", value) for value in ["480p", "720p", "1080p"]],
        ("generate_audio", True),
        ("generate_audio", False),
        ("generate_audio", None),
        ("enable_safety_checker", False),
    ],
)
def test_grok_lite_accepts_options(
    config_class: type[Any], route: str, inputs: dict[str, Any], field: str, value: Any
) -> None:
    config = config_class.model_validate(
        {
            "app_id": f"xai/grok-imagine-video/v1.5/lite/{route}",
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
        ("duration", 0),
        ("duration", 16),
        ("prompt", "x" * 4097),
        ("resolution", "4k"),
        ("seed", 1),
        ("unexpected", True),
    ],
)
def test_grok_lite_rejects_invalid_options(
    config_class: type[Any], route: str, inputs: dict[str, Any], field: str, value: Any
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_class.model_validate(
            {
                "app_id": f"xai/grok-imagine-video/v1.5/lite/{route}",
                "prompt": "A forest.",
                **inputs,
                field: value,
            }
        )


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_grok_lite_requires_prompt_and_route_inputs(
    config_class: type[Any], route: str, inputs: dict[str, Any]
) -> None:
    payload = {
        "app_id": f"xai/grok-imagine-video/v1.5/lite/{route}",
        "prompt": "A forest.",
        **inputs,
    }
    for field in ["prompt", *inputs]:
        with pytest.raises(ValidationError, match=field):
            config_class.model_validate(
                {key: value for key, value in payload.items() if key != field}
            )


@pytest.mark.parametrize(
    "aspect_ratio", ["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "21:9", "5:2"]
)
def test_grok_lite_text_to_video_accepts_aspect_ratios(aspect_ratio: str) -> None:
    config = GrokImagineVideoV15LiteTextToVideoConfig(
        app_id="xai/grok-imagine-video/v1.5/lite/text-to-video",
        prompt="A forest.",
        aspect_ratio=aspect_ratio,
    )
    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_grok_lite_rejects_aspect_ratio_outside_route_schema(
    config_class: type[Any], route: str, inputs: dict[str, Any]
) -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_class.model_validate(
            {
                "app_id": f"xai/grok-imagine-video/v1.5/lite/{route}",
                "prompt": "A forest.",
                **inputs,
                "aspect_ratio": "auto",
            }
        )


def test_grok_lite_image_to_video_accepts_openapi_optional_anchors() -> None:
    frames = [{"image_url": "https://example.com/a.png", "timestamp": i + 0.5} for i in range(4)]
    config = GrokImagineVideoV15LiteImageToVideoConfig(
        app_id="xai/grok-imagine-video/v1.5/lite/image-to-video",
        prompt="Move between anchors.",
        image_url="https://example.com/start.png",
        end_image_url="https://example.com/end.png",
        keyframes=frames,
    )
    assert config.end_image_url == "https://example.com/end.png"
    assert config.model_dump()["keyframes"] == frames


@pytest.mark.parametrize(
    "frames",
    [
        [{"image_url": "https://example.com/a.png", "timestamp": 0}],
        [{"image_url": "https://example.com/a.png", "timestamp": -0.1}],
        [{"image_url": "https://example.com/a.png", "timestamp": 6}],
        [{"image_url": "https://example.com/a.png", "timestamp": 6.1}],
        [{"image_url": "https://example.com/a.png", "timestamp": 1}] * 5,
        [{"image_url": "https://example.com/a.png"}],
        [{"timestamp": 1}],
        [{"image_url": "https://example.com/a.png", "timestamp": 1, "extra": 1}],
    ],
)
def test_grok_lite_image_to_video_rejects_invalid_anchors(frames: list[dict[str, Any]]) -> None:
    with pytest.raises(ValidationError):
        GrokImagineVideoV15LiteImageToVideoConfig(
            app_id="xai/grok-imagine-video/v1.5/lite/image-to-video",
            prompt="Move between anchors.",
            image_url="https://example.com/start.png",
            keyframes=frames,
        )


def test_grok_lite_keyframe_timestamp_uses_requested_duration() -> None:
    with pytest.raises(ValidationError, match="duration"):
        GrokImagineVideoV15LiteImageToVideoConfig(
            app_id="xai/grok-imagine-video/v1.5/lite/image-to-video",
            prompt="Move between anchors.",
            image_url="https://example.com/start.png",
            duration=1,
            keyframes=[{"image_url": "https://example.com/a.png", "timestamp": 1}],
        )
