from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, validate_parameters

PREFIX = "blackforestlabs/flux-3/"
DRAFT_INPUTS = {
    "text-to-video/draft": {},
    "image-to-video/draft": {"image_url": "https://example.com/start.png"},
    "first-last-frame-to-video/draft": {
        "start_image_url": "https://example.com/start.png",
        "end_image_url": "https://example.com/end.png",
    },
    "keyframes-to-video/draft": {
        "keyframes": [{"image_url": "https://example.com/start.png", "frame_index": 0}],
    },
    "extend-video/draft": {"video_url": "https://example.com/source.mp4"},
}
FIXED_ROUTES = {"first-last-frame-to-video/draft", "keyframes-to-video/draft"}


def parse(route: str, **parameters: object) -> BaseFalConfig:
    config = validate_parameters(
        PREFIX + route, {"prompt": "A red panda walks.", **DRAFT_INPUTS[route], **parameters}
    )
    assert config is not None
    return config


@pytest.mark.parametrize("route", DRAFT_INPUTS)
def test_drafts_accept_only_draft_defaults(route: str) -> None:
    config = parse(route)

    assert config.model_dump() == {
        "app_id": PREFIX + route,
        "prompt": "A red panda walks.",
        "aspect_ratio": "auto",
        "duration": 5 if route in FIXED_ROUTES else "auto",
        "generate_audio": True,
        "safety_tolerance": 2,
        **DRAFT_INPUTS[route],
    }
    assert config.random_seed_field is None


@pytest.mark.parametrize(
    ("route", "field"),
    [(route, field) for route, inputs in DRAFT_INPUTS.items() for field in ["prompt", *inputs]],
)
def test_drafts_require_prompt_and_route_inputs(route: str, field: str) -> None:
    parameters = {"prompt": "A red panda walks.", **DRAFT_INPUTS[route]}
    del parameters[field]

    with pytest.raises(ValidationError, match=field):
        validate_parameters(PREFIX + route, parameters)


@pytest.mark.parametrize("route", DRAFT_INPUTS)
@pytest.mark.parametrize(
    "aspect_ratio", ["auto", "21:9", "2:1", "16:9", "4:3", "1:1", "3:4", "9:16"]
)
def test_drafts_accept_aspect_ratios(route: str, aspect_ratio: str) -> None:
    assert parse(route, aspect_ratio=aspect_ratio).model_dump()["aspect_ratio"] == aspect_ratio


@pytest.mark.parametrize("route", DRAFT_INPUTS)
@pytest.mark.parametrize("duration", range(5, 21))
def test_drafts_accept_whole_second_durations(route: str, duration: int) -> None:
    assert parse(route, duration=duration).model_dump()["duration"] == duration


@pytest.mark.parametrize("route", DRAFT_INPUTS.keys() - FIXED_ROUTES)
def test_flexible_drafts_accept_auto_duration(route: str) -> None:
    assert parse(route, duration="auto").model_dump()["duration"] == "auto"


@pytest.mark.parametrize("route", FIXED_ROUTES)
def test_frame_anchored_drafts_reject_auto_duration(route: str) -> None:
    with pytest.raises(ValidationError, match="duration"):
        parse(route, duration="auto")


@pytest.mark.parametrize("route", DRAFT_INPUTS)
@pytest.mark.parametrize("safety_tolerance", [0, 4])
def test_drafts_accept_safety_bounds_and_audio_switch(route: str, safety_tolerance: int) -> None:
    config = parse(route, safety_tolerance=safety_tolerance, generate_audio=False)
    assert config.model_dump()["safety_tolerance"] == safety_tolerance
    assert config.model_dump()["generate_audio"] is False


@pytest.mark.parametrize("route", DRAFT_INPUTS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resolution", "720p"),
        ("seed", 42),
        ("aspect_ratio", "3:2"),
        ("duration", 4),
        ("duration", 21),
        ("duration", 5.5),
        ("safety_tolerance", -1),
        ("safety_tolerance", 5),
    ],
)
def test_drafts_reject_unsupported_fields_and_values(route: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(route, **{field: value})


@pytest.mark.parametrize(
    ("keyframes", "error"),
    [
        ([], "keyframes"),
        (
            [{"image_url": "https://example.com/a.png", "frame_index": i} for i in range(11)],
            "keyframes",
        ),
        ([{"image_url": "https://example.com/a.png", "frame_index": -1}], "frame_index"),
        ([{"image_url": "https://example.com/a.png", "frame_index": 121}], r"duration \* 24"),
        ([{"image_url": "https://example.com/a.png", "frame_index": 0}] * 2, "unique"),
        ([{"frame_index": 0}], "image_url"),
        ([{"image_url": "https://example.com/a.png"}], "frame_index"),
    ],
)
def test_draft_keyframes_reject_missing_or_invalid_anchors(
    keyframes: list[dict[str, object]], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        parse("keyframes-to-video/draft", keyframes=keyframes)


def test_draft_keyframes_accept_ten_anchors_including_duration_boundary() -> None:
    keyframes = [
        {"image_url": f"https://example.com/{index}.png", "frame_index": index * 48}
        for index in range(9)
    ] + [{"image_url": "https://example.com/end.png", "frame_index": 480}]
    assert (
        parse("keyframes-to-video/draft", duration=20, keyframes=keyframes).model_dump()[
            "keyframes"
        ]
        == keyframes
    )


@pytest.mark.parametrize(
    "cache_url", ["https://example.com/draft.bin", "data:application/zip;base64,AA=="]
)
def test_draft_enhance_accepts_cache_url_without_prompt(cache_url: str) -> None:
    config = validate_parameters(PREFIX + "draft-enhance", {"draft_cache_url": cache_url})
    assert config is not None
    assert config.model_dump() == {
        "app_id": PREFIX + "draft-enhance",
        "draft_cache_url": cache_url,
        "safety_tolerance": 2,
    }
    assert config.random_seed_field is None


@pytest.mark.parametrize("safety_tolerance", [0, 4])
def test_draft_enhance_accepts_safety_bounds(safety_tolerance: int) -> None:
    config = validate_parameters(
        PREFIX + "draft-enhance",
        {"draft_cache_url": "https://example.com/draft.bin", "safety_tolerance": safety_tolerance},
    )
    assert config is not None
    assert config.model_dump()["safety_tolerance"] == safety_tolerance


@pytest.mark.parametrize(
    ("parameters", "error"),
    [
        ({}, "draft_cache_url"),
        (
            {"draft_cache_url": "https://example.com/cache", "safety_tolerance": -1},
            "safety_tolerance",
        ),
        (
            {"draft_cache_url": "https://example.com/cache", "safety_tolerance": 5},
            "safety_tolerance",
        ),
        ({"draft_cache_url": "https://example.com/cache", "prompt": "Enhance"}, "prompt"),
    ],
)
def test_draft_enhance_rejects_missing_cache_and_invalid_parameters(
    parameters: dict[str, object], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        validate_parameters(PREFIX + "draft-enhance", parameters)
