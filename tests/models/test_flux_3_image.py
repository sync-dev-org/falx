from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, validate_parameters

PREFIX = "blackforestlabs/flux-3/"
ROUTES = ["text-to-image", "edit-image"]
BOX = {"x_min": 0.0, "y_min": 0.0, "x_max": 1.0, "y_max": 1.0}


def parse(route: str, **parameters: object) -> BaseFalConfig:
    inputs = {"image_urls": ["https://example.com/source.png"]} if route == "edit-image" else {}
    config = validate_parameters(PREFIX + route, {"prompt": "A red fox.", **inputs, **parameters})
    assert config is not None
    return config


@pytest.mark.parametrize("route", ROUTES)
def test_images_accept_schema_defaults(route: str) -> None:
    expected = {"image_urls": ["https://example.com/source.png"]} if route == "edit-image" else {}
    config = parse(route)

    assert config.model_dump() == {
        "app_id": PREFIX + route,
        "prompt": "A red fox.",
        "aspect_ratio": "auto",
        "resolution": "1k",
        "enable_prompt_expansion": False,
        "safety_tolerance": 2,
        "output_format": "jpeg",
        "sync_mode": False,
        "version": "latest",
        "bounding_boxes": None,
        **expected,
    }
    assert config.random_seed_field is None


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        *[
            ("aspect_ratio", ratio)
            for ratio in [
                "auto",
                "21:9",
                "2:1",
                "16:9",
                "3:2",
                "7:5",
                "4:3",
                "5:4",
                "1:1",
                "4:5",
                "3:4",
                "5:7",
                "2:3",
                "9:16",
                "1:2",
            ]
        ],
        *[("resolution", value) for value in ["768sq", "1k", "1.5k", "2k", "4k"]],
        ("output_format", "jpeg"),
        ("output_format", "png"),
        ("safety_tolerance", 0),
        ("safety_tolerance", 4),
        ("enable_prompt_expansion", True),
        ("sync_mode", True),
    ],
)
def test_images_accept_enums_bounds_and_switches(route: str, field: str, value: object) -> None:
    assert parse(route, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aspect_ratio", "6:5"),
        ("resolution", "720p"),
        ("output_format", "webp"),
        ("safety_tolerance", -1),
        ("safety_tolerance", 5),
        ("version", "old"),
        ("seed", 42),
        ("num_images", 2),
    ],
)
def test_images_reject_unsupported_fields_and_values(route: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(route, **{field: value})


@pytest.mark.parametrize(
    ("route", "parameters", "error"),
    [
        ("text-to-image", {}, "prompt"),
        ("edit-image", {"image_urls": ["https://example.com/source.png"]}, "prompt"),
        ("edit-image", {"prompt": "A red fox."}, "image_urls"),
    ],
)
def test_images_require_prompt_and_edit_references(
    route: str, parameters: dict[str, object], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        validate_parameters(PREFIX + route, parameters)


@pytest.mark.parametrize("count", [1, 10])
def test_edit_image_accepts_reference_count_bounds(count: int) -> None:
    urls = [f"https://example.com/{index}.png" for index in range(count)]
    assert parse("edit-image", image_urls=urls).model_dump()["image_urls"] == urls


@pytest.mark.parametrize("count", [0, 11])
def test_edit_image_rejects_reference_count_outside_bounds(count: int) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        parse("edit-image", image_urls=["https://example.com/input.png"] * count)


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("count", [0, 32])
def test_images_accept_layout_box_count_and_nested_bounds(route: str, count: int) -> None:
    layout = {"label": "a" * 64, "description": "x" * 500, "box": BOX}
    boxes = parse(route, bounding_boxes=[layout] * count).model_dump()["bounding_boxes"]
    assert len(boxes) == count
    for box in boxes:
        assert box["label"] == layout["label"]
        assert box["description"] == layout["description"]
        assert box["box"] == BOX


@pytest.mark.parametrize("route", ROUTES)
def test_images_accept_null_layout(route: str) -> None:
    assert parse(route, bounding_boxes=None).model_dump()["bounding_boxes"] is None


@pytest.mark.parametrize("route", ROUTES)
def test_images_reject_more_than_32_layout_boxes(route: str) -> None:
    with pytest.raises(ValidationError, match="bounding_boxes"):
        parse(route, bounding_boxes=[{"description": "fox", "box": BOX}] * 33)


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("layout", "error"),
    [
        ({"box": BOX}, "description"),
        ({"description": "x" * 501, "box": BOX}, "description"),
        ({"description": "fox", "label": "1fox", "box": BOX}, "label"),
        ({"description": "fox", "label": "a" * 65, "box": BOX}, "label"),
        ({"description": "fox", "box": {"x_min": 0, "y_min": 0, "x_max": 1}}, "y_max"),
        *[
            ({"description": "fox", "box": {**BOX, coordinate: value}}, coordinate)
            for coordinate in BOX
            for value in [-0.1, 1.1]
        ],
    ],
)
def test_images_reject_invalid_layout_details(
    route: str, layout: dict[str, object], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        parse(route, bounding_boxes=[layout])


def test_text_to_image_requires_a_box_for_each_layout_description() -> None:
    with pytest.raises(ValidationError, match="box"):
        parse("text-to-image", bounding_boxes=[{"description": "fox"}])


def test_edit_image_accepts_layout_for_reference_removal_move_and_new_objects() -> None:
    layouts = [
        {"description": "fox", "source_image_index": 0, "source_box": BOX},
        {"description": "fox", "source_image_index": 0, "source_box": BOX, "target_box": BOX},
        {"description": "new fox", "box": BOX},
    ]
    boxes = parse("edit-image", bounding_boxes=layouts).model_dump()["bounding_boxes"]
    assert boxes[0]["source_image_index"] == 0
    assert boxes[0]["source_box"] == BOX
    assert boxes[0]["target_box"] is None
    assert boxes[1]["target_box"] == BOX
    assert boxes[2]["box"] == BOX
    assert boxes[2]["source_image_index"] is None


@pytest.mark.parametrize(
    "layout",
    [
        {"description": "fox", "source_image_index": -1},
        {"description": "fox", "source_box": BOX},
    ],
)
def test_edit_image_rejects_invalid_layout_reference_index(layout: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="source_image_index"):
        parse("edit-image", bounding_boxes=[layout])
