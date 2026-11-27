from __future__ import annotations

from typing import Any, get_args

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import SUPPORTED_APP_IDS, config_class_for_app_id, validate_parameters

EDIT = "bria/fibo-2/edit"
GENERATE = "bria/fibo-2/generate"
EXPAND = "bria/fibo-edit-1.5/expand"
GUIDED = "bria/guided-remove-background"
RMBG = "bria/rmbg-3"
IMAGE = "https://example.com/image.png"
MINIMAL = {
    EDIT: {"image_urls": [IMAGE]},
    GENERATE: {},
    EXPAND: {"image_url": IMAGE},
    GUIDED: {},
    RMBG: {"image_url": IMAGE},
}
ASPECT_RATIOS = [
    "1:1",
    "1:2",
    "1:3",
    "1:4",
    "1:5",
    "2:1",
    "2:3",
    "3:1",
    "3:2",
    "3:4",
    "4:1",
    "4:3",
    "4:5",
    "5:1",
    "5:4",
    "9:16",
    "9:21",
    "10:16",
    "16:9",
    "16:10",
    "21:9",
]


def validate(app_id: str, **parameters: Any) -> Any:
    assert app_id in SUPPORTED_APP_IDS
    return validate_parameters(app_id, {**MINIMAL[app_id], **parameters})


@pytest.mark.parametrize("app_id", MINIMAL)
def test_bria_image_endpoints_are_registered_with_valid_cli_examples(app_id: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert get_args(config_class.model_fields["app_id"].annotation) == (app_id,)
    assert config_class.random_seed_field == (
        "seed" if app_id in {EDIT, GENERATE, EXPAND} else None
    )
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert validate_parameters(app_id, payload["parameters"]) is not None
    models = CliRunner().invoke(app, ["models"])
    assert models.exit_code == 0
    assert app_id in models.stdout.splitlines()


@pytest.mark.parametrize(
    ("app_id", "expected"),
    [
        (
            EDIT,
            {
                "image_urls": [IMAGE],
                "instruction": None,
                "vgl": None,
                "mask_url": None,
                "aspect_ratio": None,
                "seed": 5555,
                "sync_mode": False,
            },
        ),
        (
            GENERATE,
            {
                "prompt": None,
                "image_url": None,
                "vgl": None,
                "style": None,
                "resolution": None,
                "aspect_ratio": "1:1",
                "seed": 5555,
                "sync_mode": False,
            },
        ),
        (
            EXPAND,
            {
                "image_url": IMAGE,
                "prompt": None,
                "negative_prompt": None,
                "canvas_size": None,
                "original_image_size": None,
                "original_image_location": None,
                "aspect_ratio": None,
                "seed": None,
                "sync_mode": False,
                "return_model_output": False,
                "preserve_alpha": True,
                "retain_original_quality": True,
            },
        ),
        (
            GUIDED,
            {
                "image_url": "https://labs-assets.bria.ai/api-examples/"
                "guided-remove-background/yoga_studio_input.jpg",
                "prompt": None,
                "autocrop": False,
                "sync_mode": False,
            },
        ),
        (RMBG, {"image_url": IMAGE, "prompt": None, "sync_mode": False}),
    ],
)
def test_bria_image_defaults_follow_the_input_schema(
    app_id: str,
    expected: dict[str, Any],
) -> None:
    assert validate(app_id).model_dump(exclude={"app_id"}) == expected


@pytest.mark.parametrize("app_id", [EDIT, EXPAND, RMBG])
def test_bria_image_required_sources_are_rejected_when_missing(app_id: str) -> None:
    assert config_class_for_app_id(app_id) is not None
    with pytest.raises(ValidationError, match="image_urls|image_url"):
        validate_parameters(app_id, {})


@pytest.mark.parametrize("app_id", MINIMAL)
def test_bria_image_rejects_unknown_parameters(app_id: str) -> None:
    with pytest.raises(ValidationError, match="unexpected"):
        validate(app_id, unexpected=True)


@pytest.mark.parametrize("app_id", [EDIT, GENERATE, EXPAND])
@pytest.mark.parametrize("seed", [0, 2147483647])
def test_bria_image_accepts_seed_bounds(app_id: str, seed: int) -> None:
    assert validate(app_id, seed=seed).seed == seed


@pytest.mark.parametrize("app_id", [EDIT, GENERATE, EXPAND])
@pytest.mark.parametrize("seed", [-1, 2147483648])
def test_bria_image_rejects_seed_outside_bounds(app_id: str, seed: int) -> None:
    with pytest.raises(ValidationError, match="seed"):
        validate(app_id, seed=seed)


@pytest.mark.parametrize("app_id", [EDIT, GENERATE])
@pytest.mark.parametrize("aspect_ratio", ASPECT_RATIOS)
def test_fibo_2_accepts_documented_aspect_ratios(app_id: str, aspect_ratio: str) -> None:
    assert validate(app_id, aspect_ratio=aspect_ratio).aspect_ratio == aspect_ratio


@pytest.mark.parametrize("app_id", [EDIT, GENERATE, EXPAND])
def test_fibo_rejects_unknown_aspect_ratios(app_id: str) -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validate(app_id, aspect_ratio="7:5")


@pytest.mark.parametrize("count", [1, 4])
def test_fibo_edit_accepts_source_image_count_bounds(count: int) -> None:
    assert validate(EDIT, image_urls=[IMAGE] * count).image_urls == [IMAGE] * count


@pytest.mark.parametrize("images", [[], [IMAGE] * 5, [123]])
def test_fibo_edit_rejects_invalid_source_images(images: list[Any]) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        validate(EDIT, image_urls=images)


def test_fibo_edit_limits_masked_requests_to_one_source_image() -> None:
    assert validate(EDIT, mask_url=IMAGE).mask_url == IMAGE
    with pytest.raises(ValidationError, match="mask_url"):
        validate(EDIT, image_urls=[IMAGE, IMAGE], mask_url=IMAGE)


def test_fibo_edit_accepts_prompt_as_an_instruction_alias() -> None:
    config = validate(EDIT, prompt="Remove the vase")
    assert config.instruction == "Remove the vase"
    assert "prompt" not in config.model_dump()


def test_fibo_edit_requires_an_edit_instruction_in_a_standalone_vgl() -> None:
    config = validate(EDIT, vgl={"edit_instruction": "Remove the vase", "custom": True})
    assert config.model_dump()["vgl"]["custom"] is True
    assert validate(EDIT, instruction="Change the vase", vgl={}).vgl is not None
    with pytest.raises(ValidationError, match="edit_instruction"):
        validate(EDIT, vgl={})


@pytest.mark.parametrize("style", ["Kodak Film", "Hard Flash", "Hazy Dreamy", "Rough Realism"])
def test_fibo_generate_accepts_styles_with_a_prompt(style: str) -> None:
    assert validate(GENERATE, prompt="A vase", style=style).style == style


@pytest.mark.parametrize(
    "parameters",
    [
        {"style": "Kodak Film"},
        {"style": "Hard Flash", "prompt": "A vase", "image_url": IMAGE},
        {"style": "Hard Flash", "prompt": "A vase", "vgl": {}},
        {"vgl": {}, "image_url": IMAGE},
        {"style": "unknown", "prompt": "A vase"},
        {"resolution": "4K"},
    ],
)
def test_fibo_generate_rejects_incompatible_modes_and_invalid_choices(
    parameters: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError, match="style|image_url|resolution"):
        validate(GENERATE, **parameters)


@pytest.mark.parametrize("resolution", ["1K", "2K"])
def test_fibo_generate_accepts_resolution_choices(resolution: str) -> None:
    assert validate(GENERATE, resolution=resolution).resolution == resolution


@pytest.mark.parametrize("app_id", [EDIT, GENERATE])
def test_fibo_validates_and_serializes_nested_vgl_documents(app_id: str) -> None:
    vgl = {
        "objects": [{"relationship": "on the table", "number_of_objects": 1}],
        "text_render": [{"text": "FIBO", "color": "red"}],
        "aesthetics": {"composition": "centered"},
        "photographic_characteristics": {"focus": "sharp"},
        "lighting": {"conditions": "sunlight"},
    }
    if app_id == EDIT:
        vgl["edit_instruction"] = "Add a vase"
    config = validate(app_id, vgl=vgl)
    dumped = config.model_dump()["vgl"]
    assert dumped["objects"][0]["relationship"] == "on the table"
    assert dumped["text_render"][0]["text"] == "FIBO"
    assert dumped["lighting"]["conditions"] == "sunlight"
    assert dumped["photographic_characteristics"]["focus"] == "sharp"


@pytest.mark.parametrize("app_id", [EDIT, GENERATE])
@pytest.mark.parametrize(
    "vgl",
    [
        {"objects": [{}]},
        {"objects": [{"relationship": "on table", "number_of_objects": "several"}]},
        {"text_render": [{}]},
        {"text_render": [{"text": 12}]},
        {"lighting": {"conditions": []}},
    ],
)
def test_fibo_rejects_invalid_nested_vgl_content(app_id: str, vgl: dict[str, Any]) -> None:
    with pytest.raises(ValidationError, match="vgl"):
        parameters = {"instruction": "Edit"} if app_id == EDIT else {}
        validate(app_id, vgl=vgl, **parameters)


@pytest.mark.parametrize("field", ["canvas_size", "original_image_size", "original_image_location"])
@pytest.mark.parametrize("value", [[1], [1, 2, 3], ["wide", 100]])
def test_fibo_expand_requires_integer_pairs(field: str, value: list[Any]) -> None:
    with pytest.raises(ValidationError, match=field):
        validate(EXPAND, aspect_ratio="1:1", **{field: value})


def test_fibo_expand_checks_canvas_pairing_and_accepts_negative_placement() -> None:
    config = validate(EXPAND, canvas_size=[5000, 5000], original_image_location=[-10, -20])
    assert config.original_image_location == [-10, -20]
    for parameters in [
        {"canvas_size": [1000, 1000]},
        {"original_image_location": [0, 0]},
    ]:
        with pytest.raises(ValidationError, match="canvas_size|original_image_location"):
            validate(EXPAND, **parameters)


@pytest.mark.parametrize(
    "aspect_ratio", ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"]
)
def test_fibo_expand_aspect_ratio_overrides_source_placement(aspect_ratio: str) -> None:
    config = validate(EXPAND, aspect_ratio=aspect_ratio, original_image_location=[-10, 20])
    assert config.aspect_ratio == aspect_ratio


def test_fibo_expand_rejects_unsupported_negative_prompts() -> None:
    with pytest.raises(ValidationError, match="negative_prompt"):
        validate(EXPAND, negative_prompt="blur")


@pytest.mark.parametrize("app_id", [GUIDED, RMBG])
def test_background_removal_accepts_prompts_and_inline_images(app_id: str) -> None:
    parameters = {
        "image_url": "data:image/png;base64,aW1hZ2U=",
        "prompt": "only the chair",
        "sync_mode": True,
    }
    if app_id == GUIDED:
        parameters["autocrop"] = True
    assert validate(app_id, **parameters).model_dump(exclude={"app_id"}) == parameters
