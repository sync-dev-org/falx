from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

TEXT = "kling/v4/text-to-image"
EDIT = "kling/v4/image-to-image"
LONG = "kling/v4/long-image"
APP_IDS = (TEXT, EDIT, LONG)


def parameters(app_id: str) -> dict[str, object]:
    result: dict[str, object] = {"prompt": "An illustrated city."}
    if app_id == EDIT:
        result["image_urls"] = ["https://example.com/input.png"]
    return result


def element() -> dict[str, object]:
    return {
        "frontal_image_url": "https://example.com/front.png",
        "reference_image_urls": ["https://example.com/side.png"],
    }


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_image_endpoints_register_and_route_with_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    cls = config_class_for_app_id(app_id)
    assert cls is not None
    assert cls.random_seed_field is None
    config = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters(app_id)})
    assert type(config) is cls
    expected = {"app_id": app_id, **parameters(app_id), "sync_mode": False}
    if app_id == LONG:
        expected.update(
            skill="webpage",
            image_urls=None,
            style_image_url=None,
            subject_image_url=None,
            length="medium",
            resolution="1K",
        )
    else:
        expected.update(
            result_type="single",
            num_images=1,
            series_amount=4,
            resolution="2K",
            aspect_ratio="auto",
        )
        if app_id == EDIT:
            expected["elements"] = None
    assert config.model_dump() == expected


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_images_reject_missing_required_fields(app_id: str) -> None:
    for field in parameters(app_id):
        with pytest.raises(ValidationError, match=field):
            validate_parameters(app_id, {k: v for k, v in parameters(app_id).items() if k != field})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("at_limit", [False, True])
def test_kling_v4_images_accept_prompt_length_boundaries(app_id: str, at_limit: bool) -> None:
    length = (166000 if app_id == LONG else 50000) if at_limit else 1
    config = validate_parameters(app_id, {**parameters(app_id), "prompt": "x" * length})
    assert config is not None
    assert len(config.prompt) == length


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("too_long", [False, True])
def test_kling_v4_images_reject_empty_and_overlong_prompts(app_id: str, too_long: bool) -> None:
    length = (166001 if app_id == LONG else 50001) if too_long else 0
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(app_id, {**parameters(app_id), "prompt": "x" * length})


@pytest.mark.parametrize("app_id", (TEXT, EDIT))
@pytest.mark.parametrize("series_amount", [2, 10, "auto"])
def test_kling_v4_images_accept_series_amounts(app_id: str, series_amount: object) -> None:
    config = validate_parameters(
        app_id,
        {
            **parameters(app_id),
            "result_type": "series",
            "series_amount": series_amount,
        },
    )
    assert config is not None
    assert config.series_amount == series_amount


@pytest.mark.parametrize("app_id", (TEXT, EDIT))
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("series_amount", 1),
        ("series_amount", 11),
        ("series_amount", "manual"),
        ("series_amount", 3.5),
        ("num_images", 0),
        ("num_images", 10),
        ("result_type", "multiple"),
        ("resolution", "1080p"),
        ("aspect_ratio", "2:1"),
    ],
)
def test_kling_v4_images_reject_invalid_generation_settings(
    app_id: str,
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**parameters(app_id), field: value})


@pytest.mark.parametrize("app_id", (TEXT, EDIT))
@pytest.mark.parametrize("resolution", ["2K", "4K", "8K"])
def test_kling_v4_images_accept_resolutions_and_nine_independent_outputs(
    app_id: str,
    resolution: str,
) -> None:
    config = validate_parameters(
        app_id,
        {
            **parameters(app_id),
            "resolution": resolution,
            "num_images": 9,
            "sync_mode": True,
        },
    )
    assert config is not None
    assert config.resolution == resolution
    assert config.num_images == 9
    assert config.sync_mode is True


@pytest.mark.parametrize(
    "aspect_ratio", ["auto", "16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"]
)
def test_kling_v4_images_accept_all_aspect_ratios(aspect_ratio: str) -> None:
    config = validate_parameters(TEXT, {**parameters(TEXT), "aspect_ratio": aspect_ratio})
    assert config is not None
    assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"image_urls": []}, "image_urls"),
        ({"image_urls": ["image"] * 11}, "image_urls"),
        ({"elements": [element()] * 8}, "elements"),
        ({"elements": [{"frontal_image_url": "image"}]}, "reference_image_urls"),
        ({"elements": [{"reference_image_urls": ["image"]}]}, "frontal_image_url"),
        ({"elements": [{**element(), "reference_image_urls": []}]}, "reference_image_urls"),
        (
            {"elements": [{**element(), "reference_image_urls": ["image"] * 4}]},
            "reference_image_urls",
        ),
        ({"image_urls": ["image"] * 4, "elements": [element()] * 7}, "combined"),
    ],
)
def test_kling_v4_image_edit_rejects_invalid_references(
    updates: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(EDIT, {**parameters(EDIT), **updates})


def test_kling_v4_image_edit_accepts_ten_combined_references() -> None:
    config = validate_parameters(
        EDIT,
        {
            **parameters(EDIT),
            "image_urls": ["image"] * 3,
            "elements": [element()] * 7,
        },
    )
    assert config is not None
    assert len(config.elements) == 7
    assert config.model_dump()["elements"][0] == element()


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"skill": "other"}, "skill"),
        ({"resolution": "4K"}, "resolution"),
        ({"length": "tall"}, "length"),
        ({"skill": "ecommerce"}, "image_urls"),
        ({"skill": "ecommerce", "image_urls": []}, "image_urls"),
        ({"skill": "ecommerce", "image_urls": ["image"] * 4}, "image_urls"),
        ({"image_urls": ["image"]}, "image_urls"),
        (
            {"skill": "ecommerce", "image_urls": ["image"], "style_image_url": "style"},
            "style_image_url",
        ),
        (
            {"skill": "ecommerce", "image_urls": ["image"], "subject_image_url": "subject"},
            "subject_image_url",
        ),
    ],
)
def test_kling_v4_long_image_rejects_invalid_mode_inputs(
    updates: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(LONG, {**parameters(LONG), **updates})


@pytest.mark.parametrize("length", ["short", "medium", "long"])
def test_kling_v4_long_image_accepts_ecommerce_products_and_lengths(length: str) -> None:
    config = validate_parameters(
        LONG,
        {
            **parameters(LONG),
            "skill": "ecommerce",
            "image_urls": ["product"] * 3,
            "length": length,
            "resolution": "2K",
        },
    )
    assert config is not None
    assert config.skill == "ecommerce"
    assert len(config.image_urls) == 3
    assert config.length == length
    assert config.resolution == "2K"


def test_kling_v4_long_image_accepts_webpage_style_and_subject_references() -> None:
    config = validate_parameters(
        LONG,
        {
            **parameters(LONG),
            "style_image_url": "style",
            "subject_image_url": "subject",
        },
    )
    assert config is not None
    assert config.style_image_url == "style"
    assert config.subject_image_url == "subject"


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_image_schema_emits_valid_job_parameters(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    config = validate_parameters(app_id, payload["parameters"])
    assert config is not None
    assert config.prompt == "<your prompt here>"
    assert payload["parameters"]["resolution"] == ("1K" if app_id == LONG else "2K")


def test_kling_v4_models_command_lists_all_image_endpoints() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())
