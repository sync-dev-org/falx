from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, config_class_for_app_id, validate_parameters

TEXT_APP_IDS = [
    "openai/gpt-image-2.6/flare/text-to-image",
    "openai/gpt-image-2.6/sunburst/text-to-image",
]
EDIT_APP_IDS = [
    "openai/gpt-image-2.6/flare/edit",
    "openai/gpt-image-2.6/sunburst/edit",
]
APP_IDS = TEXT_APP_IDS + EDIT_APP_IDS


@pytest.fixture(params=APP_IDS)
def endpoint(request: pytest.FixtureRequest) -> tuple[str, dict[str, object]]:
    app_id = request.param
    assert config_class_for_app_id(app_id) is not None
    parameters: dict[str, object] = {"prompt": "A cat in a sunny garden"}
    if app_id in EDIT_APP_IDS:
        parameters["image_urls"] = ["https://example.com/input.png"]
    return app_id, parameters


def parse(endpoint: tuple[str, dict[str, object]], **overrides: object) -> BaseFalConfig:
    app_id, parameters = endpoint
    config = validate_parameters(app_id, parameters | overrides)
    assert config is not None
    return config


def test_registered_endpoints_apply_their_schema_defaults(
    endpoint: tuple[str, dict[str, object]],
) -> None:
    app_id, parameters = endpoint
    expected = {
        "app_id": app_id,
        "prompt": parameters["prompt"],
        "image_size": "landscape_4_3",
        "quality": "high",
        "reasoning_effort": "high",
        "num_images": 1,
        "output_format": "png",
        "background": "auto",
        "output_compression": None,
        "frame_count": 9,
        "frame_duration_ms": 200,
        "enable_safety_checker": True,
        "sync_mode": False,
    }
    if app_id in EDIT_APP_IDS:
        expected.update(
            image_size="auto",
            image_urls=parameters["image_urls"],
            mask_url=None,
            markup_image_url=None,
        )
    else:
        expected["svg_model"] = "gpt-6-astra"

    assert parse(endpoint).model_dump() == expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x"),
        ("prompt", "x" * 32_000),
        ("num_images", 1),
        ("num_images", 10),
        ("output_compression", None),
        ("output_compression", 0),
        ("output_compression", 100),
        ("frame_count", 2),
        ("frame_count", 16),
        ("frame_duration_ms", 20),
        ("frame_duration_ms", 2000),
        ("frame_duration_ms", 21),
        ("enable_safety_checker", False),
        ("sync_mode", True),
    ],
)
def test_accepts_parameter_boundaries_and_options(
    endpoint: tuple[str, dict[str, object]], field: str, value: object
) -> None:
    assert parse(endpoint, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("quality", ["auto", "low", "medium", "high", "xhigh", "max"]),
        ("reasoning_effort", ["low", "medium", "high"]),
        ("background", ["auto", "transparent", "opaque"]),
        ("output_format", ["jpeg", "png", "webp", "gif"]),
        (
            "image_size",
            [
                "square_hd",
                "square",
                "portrait_4_3",
                "portrait_16_9",
                "landscape_4_3",
                "landscape_16_9",
                "auto",
            ],
        ),
    ],
)
def test_accepts_all_shared_enum_choices(
    endpoint: tuple[str, dict[str, object]], field: str, values: list[str]
) -> None:
    for value in values:
        assert parse(endpoint, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", ""),
        ("prompt", "x" * 32_001),
        ("prompt", 123),
        ("num_images", 0),
        ("num_images", 11),
        ("output_compression", -1),
        ("output_compression", 101),
        ("frame_count", 1),
        ("frame_count", 17),
        ("frame_duration_ms", 19),
        ("frame_duration_ms", 2001),
        ("quality", "ultra"),
        ("reasoning_effort", "max"),
        ("background", "checkerboard"),
        ("output_format", "bmp"),
        ("image_size", "cinemascope"),
        ("unexpected", True),
    ],
)
def test_rejects_parameters_outside_the_schema(
    endpoint: tuple[str, dict[str, object]], field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(endpoint, **{field: value})


def test_rejects_missing_required_parameters(endpoint: tuple[str, dict[str, object]]) -> None:
    app_id, parameters = endpoint
    for field in parameters:
        with pytest.raises(ValidationError, match=field):
            validate_parameters(
                app_id, {key: value for key, value in parameters.items() if key != field}
            )


@pytest.mark.parametrize("dimensions", [{}, {"width": 1280, "height": 720}])
def test_accepts_explicit_image_dimensions(
    endpoint: tuple[str, dict[str, object]], dimensions: dict[str, int]
) -> None:
    expected = {"width": 512, "height": 512} | dimensions
    assert parse(endpoint, image_size=dimensions).model_dump()["image_size"] == expected


@pytest.mark.parametrize("dimension", ["width", "height"])
@pytest.mark.parametrize("value", [0, 14_143])
def test_rejects_image_dimensions_outside_the_schema(
    endpoint: tuple[str, dict[str, object]], dimension: str, value: int
) -> None:
    with pytest.raises(ValidationError, match=dimension):
        parse(endpoint, image_size={dimension: value})


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
@pytest.mark.parametrize(
    "svg_model", ["gpt-6-astra", "gpt-5.5", "gpt-5.4", "gpt-5.6-terra", "gpt-6-luna", "gpt-6-sol"]
)
def test_text_to_image_accepts_svg_models(app_id: str, svg_model: str) -> None:
    config = parse(
        (app_id, {"prompt": "A clean vector icon"}), output_format="svg", svg_model=svg_model
    )
    assert config.model_dump()["output_format"] == "svg"
    assert config.model_dump()["svg_model"] == svg_model
    assert config.model_dump()["num_images"] == 1


@pytest.mark.parametrize("app_id", TEXT_APP_IDS)
def test_text_to_image_rejects_multiple_svg_images_and_unknown_svg_models(app_id: str) -> None:
    with pytest.raises(ValidationError, match="num_images"):
        parse((app_id, {"prompt": "A vector icon"}), output_format="svg", num_images=2)
    with pytest.raises(ValidationError, match="svg_model"):
        parse((app_id, {"prompt": "A vector icon"}), svg_model="unknown")


@pytest.mark.parametrize("app_id", EDIT_APP_IDS)
def test_edit_accepts_reference_image_limits_and_optional_guidance(app_id: str) -> None:
    endpoint = (app_id, {"prompt": "Make it warm", "image_urls": []})
    for count in (0, 16):
        images = [f"https://example.com/{index}.png" for index in range(count)]
        assert parse(endpoint, image_urls=images).model_dump()["image_urls"] == images
    for field in ("mask_url", "markup_image_url"):
        url = "https://example.com/guidance.png"
        assert parse(endpoint, **{field: url}).model_dump()[field] == url


@pytest.mark.parametrize("app_id", EDIT_APP_IDS)
@pytest.mark.parametrize(
    ("parameters", "field"),
    [
        ({"image_urls": ["https://example.com/image.png"] * 17}, "image_urls"),
        ({"image_urls": [123]}, "image_urls"),
        ({"mask_url": "mask.png", "markup_image_url": "markup.png"}, "markup_image_url"),
        ({"output_format": "svg"}, "output_format"),
        ({"svg_model": "gpt-6-astra"}, "svg_model"),
    ],
)
def test_edit_rejects_invalid_references_and_unsupported_svg_options(
    app_id: str, parameters: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse((app_id, {"prompt": "Make it warm", "image_urls": []}), **parameters)
