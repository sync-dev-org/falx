from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    config_class_for_app_id,
    validate_parameters,
)

VIDEO_URL = "https://example.com/source.mp4"
APP_IDS = [
    "lightricks/ltx-2.5/alpha-gen",
    "lightricks/ltx-2.5/hdr",
    "lightricks/ltx-2.5/reframe",
    "lightricks/ltx-2.5/upscale",
]


def config_for(endpoint: str, **parameters: object) -> BaseFalConfig:
    app_id = f"lightricks/ltx-2.5/{endpoint}"
    assert app_id in SUPPORTED_APP_IDS
    config = validate_parameters(app_id, parameters)
    assert config is not None
    return config


@pytest.mark.parametrize(
    ("endpoint", "parameters", "defaults"),
    [
        ("alpha-gen", {}, {}),
        ("hdr", {}, {"output_colorspace": "acescg"}),
        (
            "reframe",
            {},
            {"aspect_ratio": "16:9", "resolution": "1080p", "placement": None},
        ),
        ("upscale", {"resolution": "1080p"}, {"resolution": "1080p"}),
    ],
)
def test_ltx_video_processing_accepts_source_video_and_schema_defaults(
    endpoint: str, parameters: dict[str, object], defaults: dict[str, object]
) -> None:
    config = config_for(endpoint, video_url=VIDEO_URL, **parameters)

    assert config.model_dump() == {
        "app_id": f"lightricks/ltx-2.5/{endpoint}",
        "video_url": VIDEO_URL,
        "enable_safety_checker": True,
        **defaults,
    }
    assert config.random_seed_field is None


@pytest.mark.parametrize("app_id", APP_IDS)
def test_ltx_video_processing_requires_source_video(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    with pytest.raises(ValidationError, match="video_url"):
        validate_parameters(app_id, {"resolution": "1080p"} if app_id.endswith("upscale") else {})


@pytest.mark.parametrize("endpoint", ["alpha-gen", "hdr", "reframe", "upscale"])
def test_ltx_video_processing_accepts_disabled_safety_checker(endpoint: str) -> None:
    parameters = {"resolution": "4k"} if endpoint == "upscale" else {}
    config = config_for(endpoint, video_url=VIDEO_URL, enable_safety_checker=False, **parameters)

    assert config.enable_safety_checker is False


@pytest.mark.parametrize("colorspace", ["acescg", "acescct", "srgb_linear", "aces2065-1"])
def test_ltx_hdr_accepts_supported_color_spaces(colorspace: str) -> None:
    config = config_for("hdr", video_url=VIDEO_URL, output_colorspace=colorspace)

    assert config.output_colorspace == colorspace


@pytest.mark.parametrize(
    ("endpoint", "parameters", "field"),
    [
        ("alpha-gen", {"video_url": 1}, "video_url"),
        ("alpha-gen", {"enable_safety_checker": "invalid"}, "enable_safety_checker"),
        ("hdr", {"output_colorspace": "rec2020"}, "output_colorspace"),
        ("reframe", {"aspect_ratio": "3:2"}, "aspect_ratio"),
        ("reframe", {"resolution": "4k"}, "resolution"),
        ("upscale", {}, "resolution"),
        ("upscale", {"resolution": "720p"}, "resolution"),
        ("hdr", {"unexpected": True}, "unexpected"),
    ],
)
def test_ltx_video_processing_rejects_invalid_parameters(
    endpoint: str, parameters: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        config_for(endpoint, **{"video_url": VIDEO_URL, **parameters})


@pytest.mark.parametrize("resolution", ["1080p", "4k", "8k"])
def test_ltx_upscale_accepts_all_target_resolutions(resolution: str) -> None:
    assert (
        config_for("upscale", video_url=VIDEO_URL, resolution=resolution).resolution == resolution
    )


@pytest.mark.parametrize(
    ("aspect_ratio", "resolution"),
    [
        ("1:1", "720x720"),
        ("1:1", "1080x1080"),
        ("4:5", "720x900"),
        ("4:5", "1080x1350"),
        ("5:4", "900x720"),
        ("5:4", "1350x1080"),
        ("9:16", "720x1280"),
        ("9:16", "1080x1920"),
        ("16:9", "1280x720"),
        ("16:9", "1920x1080"),
        ("1:1", "720p"),
        ("9:16", "1080p"),
    ],
)
def test_ltx_reframe_accepts_agreeing_dimensions_and_resolution_tiers(
    aspect_ratio: str, resolution: str
) -> None:
    config = config_for(
        "reframe", video_url=VIDEO_URL, aspect_ratio=aspect_ratio, resolution=resolution
    )

    assert config.aspect_ratio == aspect_ratio
    assert config.resolution == resolution


def test_ltx_reframe_rejects_disagreeing_explicit_dimensions_and_aspect_ratio() -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        config_for("reframe", video_url=VIDEO_URL, aspect_ratio="16:9", resolution="720x720")


@pytest.mark.parametrize("parameters", [{"resolution": "720x720"}, {"aspect_ratio": "1:1"}])
def test_ltx_reframe_only_compares_explicit_resolution_and_aspect_ratio(
    parameters: dict[str, object],
) -> None:
    config = config_for("reframe", video_url=VIDEO_URL, **parameters)

    for name, value in parameters.items():
        assert getattr(config, name) == value


@pytest.mark.parametrize(
    "anchor",
    [
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top_left",
        "top_right",
        "bottom_left",
        "bottom_right",
    ],
)
def test_ltx_reframe_accepts_source_anchors(anchor: str) -> None:
    config = config_for("reframe", video_url=VIDEO_URL, placement={"anchor": anchor})

    assert config.model_dump()["placement"] == {"anchor": anchor}


@pytest.mark.parametrize(
    "placement",
    [
        {"x": 0, "y": 0, "width": 1, "height": 1},
        {"x": 0.25, "y": 0.5, "width": 0.75, "height": 0.5},
        {"x": 0.99, "y": 0.99},
        {"x": 0, "y": 0, "width": 0.01},
        {"x": 0, "y": 0, "height": 0.01},
        {"x": 0.5, "y": 0, "width": 0.51},
        {"x": 0, "y": 0.5, "height": 0.51},
    ],
)
def test_ltx_reframe_accepts_rectangles_and_optional_dimensions(
    placement: dict[str, float],
) -> None:
    config = config_for("reframe", video_url=VIDEO_URL, placement=placement)

    assert config.model_dump()["placement"] == {"width": None, "height": None, **placement}


@pytest.mark.parametrize(
    "placement",
    [
        {},
        {"x": 0},
        {"y": 0},
        {"anchor": "outside"},
        {"anchor": "center", "x": 0, "y": 0},
        {"x": -0.01, "y": 0},
        {"x": 1, "y": 0},
        {"x": 0, "y": -0.01},
        {"x": 0, "y": 1},
        {"x": 0, "y": 0, "width": 0},
        {"x": 0, "y": 0, "width": 1.01},
        {"x": 0, "y": 0, "height": 0},
        {"x": 0, "y": 0, "height": 1.01},
        {"x": 0, "y": 0, "unexpected": True},
    ],
)
def test_ltx_reframe_rejects_invalid_placements(
    placement: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="placement"):
        config_for("reframe", video_url=VIDEO_URL, placement=placement)


def test_ltx_reframe_schema_exposes_nested_placement_constraints() -> None:
    config_class = config_class_for_app_id("lightricks/ltx-2.5/reframe")
    assert config_class is not None
    schema = config_class.model_json_schema()
    branches = schema["properties"]["placement"]["anyOf"]
    rectangle = schema["$defs"][branches[1]["$ref"].rsplit("/", 1)[-1]]

    assert rectangle["required"] == ["x", "y"]
    assert rectangle["additionalProperties"] is False
    assert rectangle["properties"]["x"]["exclusiveMaximum"] == 1
    assert rectangle["properties"]["width"]["anyOf"][0]["exclusiveMinimum"] == 0
