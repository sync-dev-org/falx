from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx import models
from falx.cli import app
from falx.models import BaseFalConfig, FalConfig, config_class_for_app_id, validate_parameters

PREFIX = "krea/v3/"
ROUTES = ["text-to-image", "text-to-image/lora", "edit", "edit/lora"]
EDIT_ROUTES = ["edit", "edit/lora"]
LORA_ROUTES = ["text-to-image/lora", "edit/lora"]
REGION = {"image_idx": 0, "x": 0, "y": 0, "width": 1, "height": 1}
runner = CliRunner()


def parse(route: str, **parameters: object) -> BaseFalConfig:
    references = {"image_urls": ["https://example.com/input.png"]} if route in EDIT_ROUTES else {}
    config = validate_parameters(
        PREFIX + route, {"prompt": "A red fox.", **references, **parameters}
    )
    assert config is not None
    return config


@pytest.mark.parametrize("route", ROUTES)
def test_krea_3_uses_endpoint_defaults(route: str) -> None:
    expected = {
        "app_id": PREFIX + route,
        "prompt": "A red fox.",
        "negative_prompt": "",
        "output_format": "png",
        "enable_safety_checker": True,
        "sync_mode": False,
        "seed": None,
        "reasoning_level": "medium",
        "image_size": "auto",
    }
    if route in EDIT_ROUTES:
        expected.update(
            image_urls=["https://example.com/input.png"], regions=None, regional_edit=None
        )
    if route in LORA_ROUTES:
        expected["loras"] = []

    assert parse(route).model_dump() == expected


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x" * 5000),
        ("negative_prompt", "x" * 1024),
        ("output_format", "jpeg"),
        ("enable_safety_checker", False),
        ("sync_mode", True),
        ("seed", -1),
        ("seed", 2**63),
        ("reasoning_level", "high"),
        *[
            ("image_size", preset)
            for preset in [
                "square_hd",
                "square",
                "portrait_4_3",
                "portrait_16_9",
                "landscape_4_3",
                "landscape_16_9",
                "auto",
            ]
        ],
        ("image_size", {"width": 1, "height": 14142}),
        ("image_size", {"width": 14142, "height": 1}),
    ],
)
def test_krea_3_preserves_valid_generation_parameters(
    route: str, field: str, value: object
) -> None:
    assert parse(route, **{field: value}).model_dump()[field] == value


@pytest.mark.parametrize("route", ROUTES)
def test_krea_3_image_size_uses_dimension_defaults(route: str) -> None:
    assert parse(route, image_size={}).model_dump()["image_size"] == {"width": 512, "height": 512}


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x" * 5001),
        ("negative_prompt", "x" * 1025),
        ("output_format", "webp"),
        ("reasoning_level", "low"),
        ("seed", "invalid"),
        ("image_size", "16:9"),
        ("image_size", None),
        ("image_size", {"width": 0}),
        ("image_size", {"height": 0}),
        ("image_size", {"width": 14143}),
        ("image_size", {"height": 14143}),
        ("num_images", 2),
    ],
)
def test_krea_3_rejects_parameters_outside_input_schema(
    route: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(route, **{field: value})


@pytest.mark.parametrize("route", ["text-to-image", "text-to-image/lora"])
@pytest.mark.parametrize("parameters", [{}, {"prompt": ""}, {"prompt": None}])
def test_krea_3_text_requires_a_nonempty_prompt(route: str, parameters: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(PREFIX + route, parameters)


@pytest.mark.parametrize("route", ["text-to-image", "text-to-image/lora"])
def test_krea_3_text_rejects_ultra_reasoning_and_edit_parameters(route: str) -> None:
    for field, value in [("reasoning_level", "ultra"), ("image_urls", []), ("regions", [])]:
        with pytest.raises(ValidationError, match=field):
            parse(route, **{field: value})


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_krea_3_edit_requires_reference_images(route: str) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        validate_parameters(PREFIX + route, {"prompt": "Make it blue."})


@pytest.mark.parametrize("route", EDIT_ROUTES)
@pytest.mark.parametrize("count", [0, 9])
def test_krea_3_edit_rejects_reference_counts_outside_bounds(route: str, count: int) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        parse(route, image_urls=["https://example.com/input.png"] * count)


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_krea_3_edit_accepts_eight_references_and_regional_preservation(route: str) -> None:
    urls = [f"https://example.com/{index}.png" for index in range(8)]
    config = parse(route, image_urls=urls, reasoning_level="ultra", regional_edit=True)
    assert config.model_dump()["image_urls"] == urls
    assert config.model_dump()["regional_edit"] is True


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_krea_3_edit_can_use_a_region_note_instead_of_the_prompt(route: str) -> None:
    config = validate_parameters(
        PREFIX + route,
        {
            "image_urls": ["https://example.com/input.png"],
            "reasoning_level": "high",
            "regions": [{**REGION, "note": "Make this blue."}],
        },
    )
    assert config is not None
    assert config.model_dump()["prompt"] == ""
    assert config.model_dump()["regions"][0]["note"] == "Make this blue."


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_krea_3_edit_requires_an_instruction_in_the_prompt_or_a_region(route: str) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        parse(route, prompt="", reasoning_level="high", regions=[REGION])


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_krea_3_edit_regions_require_high_or_ultra_reasoning(route: str) -> None:
    with pytest.raises(ValidationError, match="reasoning_level"):
        parse(route, regions=[REGION])


@pytest.mark.parametrize("route", EDIT_ROUTES)
@pytest.mark.parametrize("reasoning_level", ["high", "ultra"])
def test_krea_3_edit_accepts_region_count_and_detail_boundaries(
    route: str, reasoning_level: str
) -> None:
    region = {**REGION, "label": "a" * 64, "note": "x" * 5000}
    regions = parse(route, reasoning_level=reasoning_level, regions=[region] * 24).model_dump()[
        "regions"
    ]
    assert regions == [region] * 24


@pytest.mark.parametrize("route", EDIT_ROUTES)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("image_idx", -1),
        ("x", -0.1),
        ("x", 1),
        ("y", -0.1),
        ("y", 1),
        ("width", 0),
        ("width", 1.1),
        ("height", 0),
        ("height", 1.1),
        ("label", ""),
        ("label", "a" * 65),
        ("label", "two words"),
        ("label", "@label"),
        ("note", "x" * 5001),
    ],
)
def test_krea_3_edit_rejects_invalid_region_details(route: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        parse(route, reasoning_level="high", regions=[{**REGION, field: value}])


@pytest.mark.parametrize("route", EDIT_ROUTES)
@pytest.mark.parametrize("field", list(REGION))
def test_krea_3_edit_requires_region_coordinates_and_reference_index(
    route: str, field: str
) -> None:
    region = {key: value for key, value in REGION.items() if key != field}
    with pytest.raises(ValidationError, match=field):
        parse(route, reasoning_level="high", regions=[region])


@pytest.mark.parametrize("route", EDIT_ROUTES)
def test_krea_3_edit_rejects_more_than_24_regions(route: str) -> None:
    with pytest.raises(ValidationError, match="regions"):
        parse(route, reasoning_level="high", regions=[REGION] * 25)


@pytest.mark.parametrize("route", LORA_ROUTES)
def test_krea_3_lora_defaults_and_scale_bounds(route: str) -> None:
    paths = [f"https://example.com/{index}.safetensors" for index in range(3)]
    loras = [{"path": paths[0]}, {"path": paths[1], "scale": 0}, {"path": paths[2], "scale": 4}]
    assert parse(route, loras=loras).model_dump()["loras"] == [
        {"path": paths[0], "scale": 1},
        {"path": paths[1], "scale": 0},
        {"path": paths[2], "scale": 4},
    ]


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
def test_krea_3_lora_rejects_missing_weights_and_invalid_scales(
    route: str, loras: list[dict[str, object]], error: str
) -> None:
    with pytest.raises(ValidationError, match=error):
        parse(route, loras=loras)


@pytest.mark.parametrize("route", ["text-to-image", "edit"])
def test_krea_3_endpoints_without_lora_reject_weights(route: str) -> None:
    with pytest.raises(ValidationError, match="loras"):
        parse(route, loras=[])


@pytest.mark.parametrize(
    ("route", "class_name"),
    [
        ("text-to-image", "Krea3TextToImageConfig"),
        ("text-to-image/lora", "Krea3TextToImageLoraConfig"),
        ("edit", "Krea3EditConfig"),
        ("edit/lora", "Krea3EditLoraConfig"),
    ],
)
def test_krea_3_registry_exports_and_routes_each_config(route: str, class_name: str) -> None:
    config = parse(route)
    config_class = getattr(models, class_name)
    assert class_name in models.__all__
    assert config_class_for_app_id(PREFIX + route) is config_class
    assert isinstance(config, config_class)
    assert isinstance(TypeAdapter(FalConfig).validate_python(config.model_dump()), config_class)
    assert config_class.random_seed_field == "seed"


def test_models_command_lists_all_krea_3_endpoints() -> None:
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(result.stdout.splitlines()) >= {PREFIX + route for route in ROUTES}


@pytest.mark.parametrize("route", ROUTES)
def test_schema_command_prints_valid_krea_3_job_parameters(route: str) -> None:
    result = runner.invoke(app, ["schema", PREFIX + route])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    config = validate_parameters(payload["app_id"], payload["parameters"])
    assert config is not None
    assert config.model_dump()["image_size"] == "auto"
