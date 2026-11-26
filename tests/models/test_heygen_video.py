from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from falx.models import (
    HeygenVideoImageToVideoConfig,
    HeygenVideoReferenceToVideoConfig,
    HeygenVideoTextToVideoConfig,
)

ROUTES = [
    (HeygenVideoTextToVideoConfig, "text-to-video", {}),
    (HeygenVideoImageToVideoConfig, "image-to-video", {"image_url": "https://example.com/a.png"}),
    (HeygenVideoReferenceToVideoConfig, "reference-to-video", {}),
]


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_heygen_video_defaults(config_class: type[Any], route: str, inputs: dict[str, Any]) -> None:
    app_id = f"heygen/heygen-video/{route}"
    config = config_class.model_validate({"app_id": app_id, "prompt": "A forest.", **inputs})
    assert config.model_dump() == {
        "app_id": app_id,
        "prompt": "A forest.",
        "duration": 5,
        "resolution": "768p",
        "prompt_enhancement": "turbo",
        "enable_safety_checker": True,
        "seed": None,
        **({"aspect_ratio": "16:9"} if route == "text-to-video" else {}),
        **(
            {
                "aspect_ratio": "adaptive",
                "reference_image_urls": [],
                "reference_video_urls": [],
                "reference_audio_urls": [],
            }
            if route == "reference-to-video"
            else {}
        ),
        **inputs,
    }


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x"),
        ("prompt", "x" * 32000),
        ("duration", 5),
        ("duration", 30),
        ("seed", 0),
        ("seed", 4294967295),
        *[("resolution", value) for value in ["480p", "768p", "1080p", "2k"]],
        *[
            ("prompt_enhancement", value)
            for value in ["turbo", "quality", "ultraquality", "disabled"]
        ],
        ("enable_safety_checker", False),
    ],
)
def test_heygen_video_accepts_options(
    config_class: type[Any], route: str, inputs: dict[str, Any], field: str, value: Any
) -> None:
    config = config_class.model_validate(
        {
            "app_id": f"heygen/heygen-video/{route}",
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
        ("prompt", "x" * 32001),
        ("duration", 4),
        ("duration", 31),
        ("seed", -1),
        ("seed", 4294967296),
        ("resolution", "2K"),
        ("prompt_enhancement", "balanced"),
        ("unexpected", True),
    ],
)
def test_heygen_video_rejects_invalid_options(
    config_class: type[Any], route: str, inputs: dict[str, Any], field: str, value: Any
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_class.model_validate(
            {
                "app_id": f"heygen/heygen-video/{route}",
                "prompt": "A forest.",
                **inputs,
                field: value,
            }
        )


@pytest.mark.parametrize(("config_class", "route", "inputs"), ROUTES)
def test_heygen_video_requires_prompt_and_route_inputs(
    config_class: type[Any], route: str, inputs: dict[str, Any]
) -> None:
    payload = {"app_id": f"heygen/heygen-video/{route}", "prompt": "A forest.", **inputs}
    for field in ["prompt", *inputs]:
        with pytest.raises(ValidationError, match=field):
            config_class.model_validate(
                {key: value for key, value in payload.items() if key != field}
            )


@pytest.mark.parametrize("aspect_ratio", ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_heygen_video_accepts_aspect_ratios(aspect_ratio: str) -> None:
    for config_class, route in [
        (HeygenVideoTextToVideoConfig, "text-to-video"),
        (HeygenVideoReferenceToVideoConfig, "reference-to-video"),
    ]:
        config = config_class.model_validate(
            {
                "app_id": f"heygen/heygen-video/{route}",
                "prompt": "A forest.",
                "aspect_ratio": aspect_ratio,
            }
        )
        assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize(
    ("config_class", "route", "inputs", "aspect_ratio"),
    [
        (HeygenVideoTextToVideoConfig, "text-to-video", {}, "adaptive"),
        (HeygenVideoReferenceToVideoConfig, "reference-to-video", {}, "auto"),
        (
            HeygenVideoImageToVideoConfig,
            "image-to-video",
            {"image_url": "https://example.com/a.png"},
            "16:9",
        ),
    ],
)
def test_heygen_video_rejects_aspect_ratio_outside_route_schema(
    config_class: type[Any], route: str, inputs: dict[str, Any], aspect_ratio: str
) -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_class.model_validate(
            {
                "app_id": f"heygen/heygen-video/{route}",
                "prompt": "A forest.",
                **inputs,
                "aspect_ratio": aspect_ratio,
            }
        )


@pytest.mark.parametrize(
    ("field", "limit"),
    [
        ("reference_image_urls", 9),
        ("reference_video_urls", 3),
        ("reference_audio_urls", 3),
    ],
)
def test_heygen_video_reference_lists_respect_openapi_limits(field: str, limit: int) -> None:
    payload = {"app_id": "heygen/heygen-video/reference-to-video", "prompt": "A forest."}
    urls = ["https://example.com/reference"] * limit
    config = HeygenVideoReferenceToVideoConfig.model_validate({**payload, field: urls})
    assert getattr(config, field) == urls
    for invalid in [urls + ["https://example.com/overflow"], None]:
        with pytest.raises(ValidationError, match=field):
            HeygenVideoReferenceToVideoConfig.model_validate({**payload, field: invalid})
