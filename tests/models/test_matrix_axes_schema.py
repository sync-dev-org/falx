from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import JobConfig, MatrixAxes, MatrixAxis, validate_job_schema


def test_job_config_accepts_omitted_matrix_axes_as_single_submit_mode() -> None:
    config = JobConfig(
        app_id="fal-ai/nano-banana-2",
        parameters={"prompt": "a cat"},
        slug="demo-cat",
        version=1,
    )

    assert config.matrix_axes is None


def test_job_config_accepts_cartesian_matrix_axes() -> None:
    config = JobConfig(
        app_id="fal-ai/nano-banana-2",
        parameters={"prompt": "placeholder", "aspect_ratio": "1:1"},
        slug="demo-cat",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[
                MatrixAxis(field="prompt", values=["A", "B"]),
                MatrixAxis(field="aspect_ratio", values=["16:9", "1:1"]),
            ],
        ),
    )

    assert config.matrix_axes is not None
    assert config.matrix_axes.mode == "cartesian"
    assert len(config.matrix_axes.axes) == 2


def test_matrix_axis_accepts_multi_field_value_set() -> None:
    axis = MatrixAxis(
        fields=["edit_strength", "controls", "auto_controls"],
        value_set=[
            [0.7, None, None],
            [None, {"strength": 0.8}, None],
            [None, None, True],
        ],
    )

    assert axis.parameter_fields == ("edit_strength", "controls", "auto_controls")
    assert axis.replacement_groups == (
        (0.7, None, None),
        (None, {"strength": 0.8}, None),
        (None, None, True),
    )


def test_matrix_axes_rejects_non_cartesian_mode() -> None:
    with pytest.raises(ValidationError):
        MatrixAxes(  # type: ignore[arg-type]
            mode="zip",
            axes=[MatrixAxis(field="prompt", values=["A"])],
        )


def test_matrix_axes_rejects_empty_axes() -> None:
    with pytest.raises(ValidationError):
        MatrixAxes(mode="cartesian", axes=[])


def test_matrix_axis_rejects_empty_values() -> None:
    with pytest.raises(ValidationError):
        MatrixAxis(field="prompt", values=[])


def test_matrix_axis_rejects_empty_value_set() -> None:
    with pytest.raises(ValidationError):
        MatrixAxis(fields=["prompt"], value_set=[])


def test_matrix_axis_rejects_field_and_fields_together() -> None:
    with pytest.raises(ValidationError, match="field and fields"):
        MatrixAxis(
            field="prompt",
            fields=["prompt", "aspect_ratio"],
            values=["A"],
        )


def test_matrix_axis_rejects_fields_without_value_set() -> None:
    with pytest.raises(ValidationError, match="fields/value_set"):
        MatrixAxis(fields=["prompt"])


def test_matrix_axis_rejects_value_set_rows_that_do_not_match_fields() -> None:
    with pytest.raises(ValidationError, match="value_set item 1"):
        MatrixAxis(fields=["prompt", "aspect_ratio"], value_set=[["A"]])


def test_matrix_axes_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        MatrixAxes(  # type: ignore[call-arg]
            mode="cartesian",
            axes=[MatrixAxis(field="prompt", values=["A"])],
            unknown=True,
        )


def test_matrix_axis_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        MatrixAxis(field="prompt", values=["A"], unknown=True)  # type: ignore[call-arg]


def test_job_config_rejects_matrix_axes_field_missing_from_parameters() -> None:
    with pytest.raises(ValidationError, match="matrix_axes.axes references unknown parameter"):
        JobConfig(
            app_id="fal-ai/nano-banana-2",
            parameters={"prompt": "placeholder"},
            slug="demo-cat",
            version=1,
            matrix_axes=MatrixAxes(
                mode="cartesian",
                axes=[MatrixAxis(field="aspect_ratio", values=["16:9", "1:1"])],
            ),
        )


def test_job_config_rejects_matrix_axes_fields_missing_from_parameters() -> None:
    with pytest.raises(ValidationError, match="matrix_axes.axes references unknown parameter"):
        JobConfig(
            app_id="fal-ai/nano-banana-2",
            parameters={"prompt": "placeholder"},
            slug="demo-cat",
            version=1,
            matrix_axes=MatrixAxes(
                mode="cartesian",
                axes=[
                    MatrixAxis(
                        fields=["prompt", "aspect_ratio"],
                        value_set=[["A", "16:9"]],
                    )
                ],
            ),
        )


def test_validate_job_schema_round_trip_with_matrix_axes() -> None:
    payload = {
        "app_id": "fal-ai/nano-banana-2",
        "parameters": {"prompt": "placeholder", "aspect_ratio": "1:1"},
        "slug": "demo-cat",
        "version": 1,
        "matrix_axes": {
            "mode": "cartesian",
            "axes": [
                {"field": "prompt", "values": ["A", "B"]},
                {"field": "aspect_ratio", "values": ["16:9", "1:1"]},
            ],
        },
    }

    config = validate_job_schema(payload)

    assert config.matrix_axes is not None
    assert config.matrix_axes.axes[0].field == "prompt"
    assert config.matrix_axes.axes[1].values == ["16:9", "1:1"]


def test_validate_job_schema_round_trip_with_multi_field_matrix_axis() -> None:
    payload = {
        "app_id": "fal-ai/nano-banana-2",
        "parameters": {
            "prompt": "placeholder",
            "aspect_ratio": "1:1",
        },
        "slug": "demo-cat",
        "version": 1,
        "matrix_axes": {
            "mode": "cartesian",
            "axes": [
                {
                    "fields": ["prompt", "aspect_ratio"],
                    "value_set": [["A", "16:9"], ["B", "1:1"]],
                },
            ],
        },
    }

    config = validate_job_schema(payload)

    assert config.matrix_axes is not None
    assert config.matrix_axes.axes[0].parameter_fields == ("prompt", "aspect_ratio")
    assert config.matrix_axes.axes[0].replacement_groups == (
        ("A", "16:9"),
        ("B", "1:1"),
    )
