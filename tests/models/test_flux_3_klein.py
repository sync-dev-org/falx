from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, validate_parameters

PREFIX = "blackforestlabs/flux-3/klein/"
ROUTES = [
    "text-to-image",
    "edit-image",
    "text-to-image/lora",
    "edit-image/lora",
    "base/text-to-image/lora",
    "base/edit-image/lora",
]
TEXT_ROUTES = [route for route in ROUTES if "text-to-image" in route]
EDIT_ROUTES = [route for route in ROUTES if "edit-image" in route]
LORA_ROUTES = [route for route in ROUTES if route.endswith("/lora")]
BASE_ROUTES = [route for route in ROUTES if route.startswith("base/")]
BOX = {"x_min": 0.0, "y_min": 0.0, "x_max": 1.0, "y_max": 1.0}


def parse(route: str, **parameters: object) -> BaseFalConfig:
    references = {"image_urls": ["https://example.com/input.png"]} if route in EDIT_ROUTES else {}
    config = validate_parameters(
        PREFIX + route, {"prompt": "A red fox.", **references, **parameters}
    )
    assert config is not None
    return config


@pytest.mark.parametrize("route", ROUTES)
def test_klein_accepts_route_specific_defaults(route: str) -> None:
    expected: dict[str, object] = {
        "app_id": PREFIX + route,
        "prompt": "A red fox.",
        "enable_prompt_expansion": True,
        "seed": None,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
        "sync_mode": False,
        "image_size": None if route in EDIT_ROUTES else "square_hd",
        "bounding_boxes": None,
    }
    if route in EDIT_ROUTES:
        expected["image_urls"] = ["https://example.com/input.png"]
    if route in LORA_ROUTES:
        expected["loras"] = []
    if route in BASE_ROUTES:
        expected.update(negative_prompt="", num_inference_steps=50, guidance_scale=3.5)

    config = parse(route)
    assert config.model_dump() == expected
    assert config.random_seed_field == "seed"


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed", -1),
        ("seed", 2**63),
        ("num_images", 1),
        ("num_images", 4),
        ("output_format", "jpeg"),
        ("output_format", "webp"),
        ("enable_prompt_expansion", False),
        ("enable_safety_checker", False),
        ("sync_mode", True),
        *[
            ("image_size", preset)
            for preset in [
                "square_hd",
                "square",
                "portrait_4_3",
                "portrait_16_9",
                "landscape_4_3",
                "landscape_16_9",
            ]
        ],
        ("image_size", {"width": 256, "height": 4096}),
        ("image_size", {}),
    ],
)
def test_klein_accepts_image_parameters(route: str, field: str, value: object) -> None:
    expected = {"width": 512, "height": 512} if value == {} else value
    assert parse(route, **{field: value}).model_dump()[field] == expected


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("num_images", 0),
        ("num_images", 5),
        ("output_format", "gif"),
        ("image_size", "auto"),
        ("image_size", {"width": 0}),
        ("image_size", {"height": 14143}),
        ("resolution", "4k"),
    ],
)
def test_klein_rejects_unsupported_values(route: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(route, **{field: value})


@pytest.mark.parametrize("route", ROUTES)
def test_klein_requires_prompt(route: str) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(PREFIX + route, {"image_urls": ["https://example.com/input.png"]})


@pytest.mark.parametrize("route", TEXT_ROUTES)
def test_klein_text_rejects_null_image_size(route: str) -> None:
    with pytest.raises(ValidationError, match="image_size"):
        parse(route, image_size=None)


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_klein_edits_require_references(route: str) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        validate_parameters(PREFIX + route, {"prompt": "A red fox."})


@pytest.mark.parametrize("route", EDIT_ROUTES)
@pytest.mark.parametrize("count", [1, 10])
def test_klein_edits_accept_reference_count_bounds(route: str, count: int) -> None:
    urls = [f"https://example.com/{index}.png" for index in range(count)]
    assert parse(route, image_urls=urls, image_size=None).model_dump()["image_urls"] == urls


@pytest.mark.parametrize("route", EDIT_ROUTES)
@pytest.mark.parametrize("count", [0, 11])
def test_klein_edits_reject_reference_count_outside_bounds(route: str, count: int) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        parse(route, image_urls=["https://example.com/input.png"] * count)


@pytest.mark.parametrize("route", LORA_ROUTES)
@pytest.mark.parametrize("scale", [0.0, 4.0])
def test_klein_loras_accept_three_weights_and_scale_bounds(route: str, scale: float) -> None:
    loras = [
        {"path": f"https://example.com/{index}.safetensors", "scale": scale} for index in range(3)
    ]
    assert parse(route, loras=loras).model_dump()["loras"] == loras


@pytest.mark.parametrize("route", LORA_ROUTES)
def test_klein_loras_default_scale_and_do_not_share_mutable_defaults(route: str) -> None:
    first = parse(route)
    second = parse(route)
    first.loras.append({"path": "https://example.com/first.safetensors"})
    assert second.model_dump()["loras"] == []
    assert parse(route, loras=[{"path": "https://example.com/style.safetensors"}]).model_dump()[
        "loras"
    ] == [{"path": "https://example.com/style.safetensors", "scale": 1.0}]


@pytest.mark.parametrize("route", LORA_ROUTES)
@pytest.mark.parametrize(
    ("loras", "error"),
    [
        ([{"scale": 1}], "path"),
        ([{"path": "https://example.com/style.safetensors", "scale": -0.1}], "scale"),
        ([{"path": "https://example.com/style.safetensors", "scale": 4.1}], "scale"),
        ([{"path": "https://example.com/style.safetensors"}] * 4, "loras"),
    ],
)
def test_klein_loras_reject_missing_path_and_invalid_weights(
    route: str, loras: list[dict[str, object]], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        parse(route, loras=loras)


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [("negative_prompt", "blur"), ("num_inference_steps", 4), ("guidance_scale", 0.0)],
)
def test_only_base_lora_routes_offer_inference_controls(
    route: str, field: str, value: object
) -> None:
    if route in BASE_ROUTES:
        assert parse(route, **{field: value}).model_dump()[field] == value
    else:
        with pytest.raises(ValidationError, match=field):
            parse(route, **{field: value})


@pytest.mark.parametrize("route", ["text-to-image", "edit-image"])
def test_klein_without_lora_rejects_weights(route: str) -> None:
    with pytest.raises(ValidationError, match="loras"):
        parse(route, loras=[])


@pytest.mark.parametrize("route", BASE_ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("num_inference_steps", 3),
        ("num_inference_steps", 51),
        ("guidance_scale", -0.1),
        ("guidance_scale", 20.1),
    ],
)
def test_klein_base_rejects_inference_controls_outside_bounds(
    route: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(route, **{field: value})


@pytest.mark.parametrize("route", BASE_ROUTES)
def test_klein_base_accepts_upper_inference_bounds(route: str) -> None:
    config = parse(route, num_inference_steps=50, guidance_scale=20, negative_prompt="blur")
    assert config.model_dump()["guidance_scale"] == 20
    assert config.model_dump()["negative_prompt"] == "blur"


@pytest.mark.parametrize("route", ROUTES)
def test_klein_accepts_layout_coordinates_and_label_limits(route: str) -> None:
    layout = {"label": "a" * 64, "description": "x" * 500, "box": BOX}
    boxes = parse(route, bounding_boxes=[layout] * 32).model_dump()["bounding_boxes"]
    assert len(boxes) == 32
    assert boxes[0]["box"] == BOX
    assert boxes[0]["label"] == "a" * 64
    assert boxes[0]["description"] == "x" * 500


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("layout", "error"),
    [
        ({"box": BOX}, "description"),
        ({"description": "x" * 501, "box": BOX}, "description"),
        ({"description": "fox", "label": "1fox", "box": BOX}, "label"),
        ({"description": "fox", "label": "a" * 65, "box": BOX}, "label"),
        ({"description": "fox", "box": {**BOX, "x_min": -0.1}}, "x_min"),
        ({"description": "fox", "box": {**BOX, "y_max": 1.1}}, "y_max"),
        ({"description": "fox", "box": {"x_min": 0, "y_min": 0, "x_max": 1}}, "y_max"),
    ],
)
def test_klein_rejects_invalid_layout_details(
    route: str, layout: dict[str, object], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        parse(route, bounding_boxes=[layout])


@pytest.mark.parametrize("route", ROUTES)
def test_klein_rejects_more_than_32_layout_boxes(route: str) -> None:
    with pytest.raises(ValidationError, match="bounding_boxes"):
        parse(route, bounding_boxes=[{"description": "fox", "box": BOX}] * 33)


@pytest.mark.parametrize("route", TEXT_ROUTES)
def test_klein_text_requires_a_box_for_each_layout_description(route: str) -> None:
    with pytest.raises(ValidationError, match="box"):
        parse(route, bounding_boxes=[{"description": "fox"}])


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_klein_edit_accepts_reference_layout_for_move_or_removal(route: str) -> None:
    layouts = [
        {"description": "fox", "source_image_index": 0, "source_box": BOX},
        {"description": "fox", "source_image_index": 0, "source_box": BOX, "target_box": BOX},
        {"description": "new fox", "box": BOX},
    ]
    boxes = parse(route, bounding_boxes=layouts).model_dump()["bounding_boxes"]
    assert boxes[0]["source_box"] == BOX
    assert boxes[0]["target_box"] is None
    assert boxes[1]["target_box"] == BOX
    assert boxes[2]["source_image_index"] is None


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_klein_edit_rejects_negative_reference_index(route: str) -> None:
    with pytest.raises(ValidationError, match="source_image_index"):
        parse(route, bounding_boxes=[{"description": "fox", "source_image_index": -1}])


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_klein_edit_source_box_requires_reference_index(route: str) -> None:
    with pytest.raises(ValidationError, match="source_image_index"):
        parse(route, bounding_boxes=[{"description": "fox", "source_box": BOX}])
