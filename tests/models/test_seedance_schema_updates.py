from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import config_class_for_app_id, validate_parameters

SEEDANCE2_APP_IDS = tuple(
    f"bytedance/seedance-2.0/{tier}{mode}-to-video"
    for tier in ("", "fast/", "mini/")
    for mode in ("text", "image", "reference")
)
SEEDANCE25_APP_IDS = tuple(
    f"bytedance/seedance-2.5/{mode}-to-video" for mode in ("text", "image", "reference")
)
UPDATED_APP_IDS = SEEDANCE2_APP_IDS + SEEDANCE25_APP_IDS
REFERENCE_APP_ID = SEEDANCE25_APP_IDS[2]


def minimal_parameters(app_id: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": "A crane flies over a lake."}
    if app_id.endswith("/image-to-video"):
        parameters["image_url"] = "https://example.com/start.png"
    return parameters


@pytest.mark.parametrize("app_id", SEEDANCE2_APP_IDS)
def test_seedance2_omits_unsupported_seed_from_request_and_randomization(app_id: str) -> None:
    config = validate_parameters(app_id, minimal_parameters(app_id))

    assert "seed" not in config.model_dump(exclude={"app_id"}, exclude_none=True)
    assert type(config).random_seed_field is None
    with pytest.raises(ValidationError, match="seed"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "seed": 42})


@pytest.mark.parametrize("app_id", UPDATED_APP_IDS)
@pytest.mark.parametrize("codec", ["auto", "H264", "H265"])
def test_seedance_preserves_codec_and_last_frame_options(app_id: str, codec: str) -> None:
    config = validate_parameters(
        app_id,
        {**minimal_parameters(app_id), "codec": codec, "return_last_frame": True},
    )

    arguments = config.model_dump(exclude={"app_id"}, exclude_none=True)
    assert arguments["codec"] == codec
    assert arguments["return_last_frame"] is True


@pytest.mark.parametrize("app_id", UPDATED_APP_IDS)
@pytest.mark.parametrize(("field", "value"), [("codec", "AV1"), ("return_last_frame", None)])
def test_seedance_rejects_invalid_output_options(app_id: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**minimal_parameters(app_id), field: value})


@pytest.mark.parametrize(
    "app_id", [app_id for app_id in SEEDANCE2_APP_IDS if "/reference-" in app_id]
)
@pytest.mark.parametrize("duration", ["auto", *(str(value) for value in range(4, 16))])
def test_seedance2_preserves_duration_strings_in_requests(app_id: str, duration: str) -> None:
    config = validate_parameters(app_id, {**minimal_parameters(app_id), "duration": duration})

    assert config.model_dump()["duration"] == duration


@pytest.mark.parametrize("app_id", SEEDANCE2_APP_IDS)
def test_seedance2_rejects_integer_durations(app_id: str) -> None:
    with pytest.raises(ValidationError, match="duration"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "duration": 4})


@pytest.mark.parametrize(
    "app_id", [app_id for app_id in SEEDANCE2_APP_IDS if "/reference-" in app_id]
)
@pytest.mark.parametrize("duration", ["3", "16"])
def test_seedance2_reference_rejects_out_of_range_durations(app_id: str, duration: str) -> None:
    with pytest.raises(ValidationError, match="duration"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "duration": duration})


@pytest.mark.parametrize("app_id", SEEDANCE25_APP_IDS)
@pytest.mark.parametrize("output_format", ["mp4", "mov"])
def test_seedance25_preserves_4k_draft_and_output_format(app_id: str, output_format: str) -> None:
    config = validate_parameters(
        app_id,
        {
            **minimal_parameters(app_id),
            "resolution": "4k",
            "draft": True,
            "output_format": output_format,
        },
    )

    arguments = config.model_dump(exclude={"app_id"}, exclude_none=True)
    assert arguments["resolution"] == "4k"
    assert arguments["draft"] is True
    assert arguments["output_format"] == output_format


@pytest.mark.parametrize("app_id", SEEDANCE25_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [("draft", None), ("output_format", "webm")],
)
def test_seedance25_rejects_invalid_draft_and_format_options(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**minimal_parameters(app_id), field: value})


@pytest.mark.parametrize("app_id", SEEDANCE25_APP_IDS[1:])
@pytest.mark.parametrize("parameters", [{}, {"prompt": None}])
def test_seedance25_image_and_reference_allow_omitted_or_null_prompt(
    app_id: str, parameters: dict[str, object]
) -> None:
    if app_id.endswith("/image-to-video"):
        parameters = {**parameters, "image_url": "https://example.com/start.png"}
    config = validate_parameters(app_id, parameters)

    assert config.model_dump()["prompt"] is None
    assert "prompt" not in config_class_for_app_id(app_id).model_json_schema().get("required", [])


@pytest.mark.parametrize("task", ["auto", "reference", "editing", "extension"])
@pytest.mark.parametrize("seed", [None, -1, 42, 2**40])
def test_seedance25_reference_preserves_task_and_nullable_seed(task: str, seed: int | None) -> None:
    config = validate_parameters(REFERENCE_APP_ID, {"task": task, "seed": seed})

    assert config.model_dump()["task"] == task
    assert config.model_dump()["seed"] == seed
    assert type(config).random_seed_field == "seed"


@pytest.mark.parametrize(("field", "value"), [("task", "extend"), ("seed", "invalid")])
def test_seedance25_reference_rejects_invalid_task_and_seed(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(REFERENCE_APP_ID, {field: value})


@pytest.mark.parametrize(
    "app_id",
    (
        *UPDATED_APP_IDS,
        "bytedance/seedance-2.5/flash/reference-to-video",
        "bytedance/seedance-2.5/us/reference-to-video",
    ),
)
def test_seedance_schema_prints_valid_job_yaml_for_current_inputs(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    job = YAML(typ="safe").load(result.stdout)
    assert job["app_id"] == app_id
    config = validate_parameters(app_id, job["parameters"])
    assert config.model_dump(exclude={"app_id"}) == job["parameters"]
