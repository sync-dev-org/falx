from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from falx.matrix import (
    CompiledCell,
    MatrixValidationError,
    cell_is_completed,
    cell_subdir_name,
    compile_cells,
    compiled_child_payload,
    pending_cells,
    validate_matrix,
    validate_matrix_or_raise,
    write_compiled_child,
)
from falx.models import JobConfig, MatrixAxes, MatrixAxis

_SAFE_YAML = YAML(typ="safe")


def _config_with_matrix() -> JobConfig:
    return JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
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


def _config_with_multi_field_matrix() -> JobConfig:
    return JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
        parameters={
            "prompt": "placeholder",
            "aspect_ratio": "1:1",
            "resolution": "480p",
        },
        slug="demo-cat",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[
                MatrixAxis(
                    fields=["prompt", "aspect_ratio"],
                    value_set=[["A", "16:9"], ["B", "1:1"]],
                ),
                MatrixAxis(field="resolution", values=["480p", "720p"]),
            ],
        ),
    )


def _config_single() -> JobConfig:
    return JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
        parameters={"prompt": "single"},
        slug="demo-cat",
        version=1,
    )


def test_cell_subdir_name_rejects_non_positive_cell() -> None:
    with pytest.raises(ValueError):
        cell_subdir_name(0, 1, 1)
    with pytest.raises(ValueError):
        cell_subdir_name(-1, 1, 1)


def test_cell_subdir_name_includes_cell_version_take_axes() -> None:
    assert cell_subdir_name(1, 1, 1) == "c1-v1-1"
    assert cell_subdir_name(2, 3, 4) == "c2-v3-4"
    assert cell_subdir_name(42, 2, 3) == "c42-v2-3"


def test_cell_subdir_name_defaults_take_to_one() -> None:
    assert cell_subdir_name(1, 1) == "c1-v1-1"


def test_compile_cells_returns_empty_for_single_submit_mode() -> None:
    assert compile_cells(_config_single()) == []


def test_compile_cells_expands_cartesian_product_in_row_major_order() -> None:
    cells = compile_cells(_config_with_matrix())

    assert [(cell.cell, cell.coords) for cell in cells] == [
        (1, {"prompt": "A", "aspect_ratio": "16:9"}),
        (2, {"prompt": "A", "aspect_ratio": "1:1"}),
        (3, {"prompt": "B", "aspect_ratio": "16:9"}),
        (4, {"prompt": "B", "aspect_ratio": "1:1"}),
    ]


def test_compile_cells_expands_multi_field_axis_as_synchronized_units() -> None:
    cells = compile_cells(_config_with_multi_field_matrix())

    assert [(cell.cell, cell.coords) for cell in cells] == [
        (1, {"prompt": "A", "aspect_ratio": "16:9", "resolution": "480p"}),
        (2, {"prompt": "A", "aspect_ratio": "16:9", "resolution": "720p"}),
        (3, {"prompt": "B", "aspect_ratio": "1:1", "resolution": "480p"}),
        (4, {"prompt": "B", "aspect_ratio": "1:1", "resolution": "720p"}),
    ]


def test_compile_cells_skips_none_values_in_multi_field_axis() -> None:
    config = JobConfig(
        app_id="fal-ai/nano-banana-2",
        parameters={
            "prompt": "placeholder",
            "edit_strength": 0.2,
            "controls": {"strength": 0.1},
            "auto_controls": False,
        },
        slug="route-demo",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[
                MatrixAxis(
                    fields=["edit_strength", "controls", "auto_controls"],
                    value_set=[
                        [0.7, None, None],
                        [None, {"strength": 0.8}, None],
                        [None, None, True],
                    ],
                )
            ],
        ),
    )

    cells = compile_cells(config)

    assert cells[0].coords == {
        "edit_strength": 0.7,
        "controls": None,
        "auto_controls": None,
    }
    assert cells[0].parameters == {
        "prompt": "placeholder",
        "edit_strength": 0.7,
        "controls": {"strength": 0.1},
        "auto_controls": False,
    }
    assert cells[1].parameters == {
        "prompt": "placeholder",
        "edit_strength": 0.2,
        "controls": {"strength": 0.8},
        "auto_controls": False,
    }
    assert cells[2].parameters == {
        "prompt": "placeholder",
        "edit_strength": 0.2,
        "controls": {"strength": 0.1},
        "auto_controls": True,
    }


def test_compile_cells_substitutes_coords_into_per_cell_parameters() -> None:
    cells = compile_cells(_config_with_matrix())

    assert cells[0].parameters == {"prompt": "A", "aspect_ratio": "16:9"}
    assert cells[1].parameters == {"prompt": "A", "aspect_ratio": "1:1"}
    assert cells[3].parameters == {"prompt": "B", "aspect_ratio": "1:1"}


def test_compile_cells_does_not_mutate_source_parameters() -> None:
    config = _config_with_matrix()
    original_parameters = dict(config.parameters)

    compile_cells(config)

    assert config.parameters == original_parameters


def test_compiled_child_payload_strips_matrix_axes_and_pins_iterations_to_one() -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)

    payload = compiled_child_payload(config, cells[0])

    assert "matrix_axes" not in payload
    assert payload["iterations"] == 1
    assert payload["app_id"] == config.app_id
    assert payload["parameters"] == {"prompt": "A", "aspect_ratio": "16:9"}
    assert payload["slug"] == "demo-cat"
    assert payload["version"] == 1


def test_compiled_child_payload_routes_output_dir_into_cell_version_take_subdir() -> None:
    config = JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
        parameters={"prompt": "p", "aspect_ratio": "1:1"},
        output_dir="workspace/demo/exp/G-0001_demo/output",
        slug="demo-cat",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[MatrixAxis(field="prompt", values=["A", "B"])],
        ),
    )
    cells = compile_cells(config)

    payload = compiled_child_payload(config, cells[1], take=1)

    assert payload["output_dir"] == "workspace/demo/exp/G-0001_demo/output/c2-v1-1"


def test_compiled_child_payload_omits_output_dir_when_parent_omits_it() -> None:
    cells = compile_cells(_config_with_matrix())

    payload = compiled_child_payload(_config_with_matrix(), cells[0])

    assert "output_dir" not in payload


def test_compiled_child_payload_round_trips_through_validate_job_schema() -> None:
    from falx.models import validate_job_schema

    config = _config_with_matrix()
    cells = compile_cells(config)
    for cell in cells:
        payload = compiled_child_payload(config, cell)
        round_tripped = validate_job_schema(payload)
        assert round_tripped.matrix_axes is None
        assert round_tripped.iterations == 1


def test_write_compiled_child_materializes_yaml_under_cell_subdir(tmp_path: Path) -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0003_demo-cat" / "output"

    child_path = write_compiled_child(config=config, cell=cells[2], output_dir=output_dir)

    assert child_path == output_dir / "c3-v1-1" / "G-0003_c3-v1-1-job.yaml"
    assert child_path.is_file()
    loaded = _SAFE_YAML.load(child_path.read_text())
    assert loaded["parameters"] == {"prompt": "B", "aspect_ratio": "16:9"}
    assert loaded["iterations"] == 1
    assert "matrix_axes" not in loaded


def test_validate_matrix_returns_empty_summary_for_single_submit_mode() -> None:
    summary = validate_matrix(_config_single())

    assert summary.cell_results == []
    assert summary.ok is True


def test_validate_matrix_marks_all_cells_ok_for_well_formed_matrix() -> None:
    summary = validate_matrix(_config_with_matrix())

    assert summary.ok is True
    assert len(summary.cell_results) == 4
    assert all(result.error is None for result in summary.cell_results)


def test_validate_matrix_accepts_multi_field_axis_cells() -> None:
    summary = validate_matrix(_config_with_multi_field_matrix())

    assert summary.ok is True
    assert [result.coords for result in summary.cell_results] == [
        {"prompt": "A", "aspect_ratio": "16:9", "resolution": "480p"},
        {"prompt": "A", "aspect_ratio": "16:9", "resolution": "720p"},
        {"prompt": "B", "aspect_ratio": "1:1", "resolution": "480p"},
        {"prompt": "B", "aspect_ratio": "1:1", "resolution": "720p"},
    ]


def test_validate_matrix_or_raise_passes_through_when_all_cells_ok() -> None:
    summary = validate_matrix_or_raise(_config_with_matrix())

    assert summary.ok is True


def test_matrix_validation_error_exposes_summary_attribute() -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)
    summary = validate_matrix(config)
    failed_result = summary.cell_results[0].__class__(
        cell=cells[0].cell,
        coords=cells[0].coords,
        ok=False,
        error="forced",
    )
    bad_summary = summary.__class__(cell_results=[failed_result])

    error = MatrixValidationError(bad_summary)

    assert error.summary is bad_summary
    assert "1/1" in str(error)


def test_cell_is_completed_false_when_only_child_yaml_present(tmp_path: Path) -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0007_matrix-demo" / "output"
    child_path = write_compiled_child(config=config, cell=cells[0], output_dir=output_dir)

    assert child_path.name == "G-0007_c1-v1-1-job.yaml"
    cell_dir = output_dir / cell_subdir_name(cells[0].cell, config.version, take=1)
    assert cell_is_completed(cell_dir) is False


def test_cell_is_completed_true_when_wrapper_output_file_present(tmp_path: Path) -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)
    write_compiled_child(config=config, cell=cells[0], output_dir=tmp_path)

    output_file = (
        tmp_path
        / cell_subdir_name(cells[0].cell, config.version, take=1)
        / "out.png"
    )
    output_file.write_bytes(b"fake bytes")

    assert cell_is_completed(output_file.parent) is True


def test_cell_is_completed_false_when_cell_dir_missing(tmp_path: Path) -> None:
    assert cell_is_completed(tmp_path / "c999-v1-1") is False


def test_pending_cells_excludes_already_completed_cells_in_order(tmp_path: Path) -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)

    # Pre-materialize c2-v1-1 as completed
    write_compiled_child(config=config, cell=cells[1], output_dir=tmp_path)
    output_file = (
        tmp_path / cell_subdir_name(cells[1].cell, config.version, take=1) / "out.png"
    )
    output_file.write_bytes(b"fake")

    pending = pending_cells(
        cells=cells, output_dir=tmp_path, version=config.version, take=1
    )

    assert [cell.cell for cell in pending] == [1, 3, 4]


def test_pending_cells_returns_all_cells_when_no_output_dir_exists(tmp_path: Path) -> None:
    config = _config_with_matrix()
    cells = compile_cells(config)

    pending = pending_cells(
        cells=cells,
        output_dir=tmp_path / "absent",
        version=config.version,
        take=1,
    )

    assert [cell.cell for cell in pending] == [1, 2, 3, 4]


def test_compiled_cell_is_frozen() -> None:
    cell = CompiledCell(cell=1, coords={"prompt": "A"}, parameters={"prompt": "A"})

    with pytest.raises(dataclasses.FrozenInstanceError):
        cell.cell = 2  # type: ignore[misc]


def _config_with_url_axis(image_urls: list[str]) -> JobConfig:
    return JobConfig(
        app_id="bytedance/seedance-2.0/image-to-video",
        parameters={"prompt": "go", "image_url": "placeholder"},
        slug="demo-i2v",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[MatrixAxis(field="image_url", values=image_urls)],
        ),
    )


def test_validate_matrix_marks_cell_with_missing_local_url_file_as_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = tmp_path / "exists.png"
    existing.write_bytes(b"payload")
    monkeypatch.chdir(tmp_path)
    config = _config_with_url_axis(["exists.png", "missing.png"])

    summary = validate_matrix(config)

    assert summary.ok is False
    assert summary.cell_results[0].ok is True
    assert summary.cell_results[1].ok is False
    assert "URL fields must be public URLs or local file paths" in (
        summary.cell_results[1].error or ""
    )


def test_validate_matrix_accepts_cells_with_existing_local_url_files_resolved_via_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(b"a")
    second.write_bytes(b"b")
    monkeypatch.chdir(tmp_path)
    config = _config_with_url_axis(["first.png", "second.png"])

    summary = validate_matrix(config)

    assert summary.ok is True
    assert [result.cell for result in summary.cell_results] == [1, 2]


def test_validate_matrix_accepts_public_url_in_url_axis(tmp_path: Path) -> None:
    config = _config_with_url_axis(
        ["https://example.com/a.png", "https://example.com/b.png"],
    )

    summary = validate_matrix(config)

    assert summary.ok is True


def test_validate_matrix_marks_cell_with_invalid_wrapper_constraint_as_failed() -> None:
    config = JobConfig(
        app_id="luma/agent/ray/v3.2/text-to-video",
        parameters={"prompt": "p", "resolution": "540p"},
        slug="demo-luma",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[MatrixAxis(field="resolution", values=["540p", "9999p"])],
        ),
    )

    summary = validate_matrix(config)

    assert summary.ok is False
    assert summary.cell_results[0].ok is True
    assert summary.cell_results[1].ok is False
    assert summary.cell_results[1].error is not None


def test_validate_matrix_or_raise_includes_url_failures_in_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    config = _config_with_url_axis(["missing-a.png", "missing-b.png"])

    with pytest.raises(MatrixValidationError) as excinfo:
        validate_matrix_or_raise(config)

    assert len(excinfo.value.summary.failed) == 2


def _config_with_matrix_versioned(version: int) -> JobConfig:
    return JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
        parameters={"prompt": "placeholder", "aspect_ratio": "1:1"},
        slug="demo-cat",
        version=version,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[
                MatrixAxis(field="prompt", values=["A", "B"]),
                MatrixAxis(field="aspect_ratio", values=["16:9", "1:1"]),
            ],
        ),
    )


def test_cell_subdir_name_without_zero_padding() -> None:
    assert cell_subdir_name(1, 1, 1) == "c1-v1-1"
    assert cell_subdir_name(42, 2, 3) == "c42-v2-3"
    assert cell_subdir_name(123, 3, 12) == "c123-v3-12"


def test_cell_subdir_name_rejects_non_positive_version() -> None:
    with pytest.raises(ValueError):
        cell_subdir_name(1, 0, 1)
    with pytest.raises(ValueError):
        cell_subdir_name(1, -1, 1)


def test_cell_subdir_name_rejects_non_positive_take() -> None:
    with pytest.raises(ValueError):
        cell_subdir_name(1, 1, 0)
    with pytest.raises(ValueError):
        cell_subdir_name(1, 1, -1)


def test_compiled_child_payload_routes_output_dir_into_cell_version_take_subdir_v1() -> None:
    config = JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
        parameters={"prompt": "p", "aspect_ratio": "1:1"},
        output_dir="workspace/demo/exp/G-0001_demo/output",
        slug="demo-cat",
        version=1,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[MatrixAxis(field="prompt", values=["A", "B"])],
        ),
    )
    cells = compile_cells(config)

    payload = compiled_child_payload(config, cells[1], take=1)

    assert payload["output_dir"] == "workspace/demo/exp/G-0001_demo/output/c2-v1-1"


def test_compiled_child_payload_routes_output_dir_into_cell_version_take_subdir_v2() -> None:
    config = JobConfig(
        app_id="bytedance/seedance-2.0/text-to-video",
        parameters={"prompt": "p", "aspect_ratio": "1:1"},
        output_dir="workspace/demo/exp/G-0001_demo/output",
        slug="demo-cat",
        version=2,
        matrix_axes=MatrixAxes(
            mode="cartesian",
            axes=[MatrixAxis(field="prompt", values=["A", "B"])],
        ),
    )
    cells = compile_cells(config)

    payload = compiled_child_payload(config, cells[0], take=3)

    assert payload["output_dir"] == "workspace/demo/exp/G-0001_demo/output/c1-v2-3"


def test_write_compiled_child_materializes_yaml_under_versioned_cell_subdir(
    tmp_path: Path,
) -> None:
    config = _config_with_matrix_versioned(version=2)
    cells = compile_cells(config)
    output_dir = tmp_path / "workspace" / "demo" / "exp" / "G-0005_demo-cat" / "output"

    child_path = write_compiled_child(
        config=config, cell=cells[2], output_dir=output_dir, take=1
    )

    assert child_path == output_dir / "c3-v2-1" / "G-0005_c3-v2-1-job.yaml"
    assert child_path.is_file()


def test_pending_cells_excludes_completed_cells_within_same_version(tmp_path: Path) -> None:
    config = _config_with_matrix_versioned(version=1)
    cells = compile_cells(config)

    # Pre-materialize c2-v1-1 as completed
    cell_dir = tmp_path / cell_subdir_name(cells[1].cell, config.version, take=1)
    cell_dir.mkdir(parents=True)
    (cell_dir / "out.png").write_bytes(b"fake")

    pending = pending_cells(
        cells=cells, output_dir=tmp_path, version=config.version, take=1
    )

    assert [cell.cell for cell in pending] == [1, 3, 4]


def test_pending_cells_treats_new_version_as_fully_pending(tmp_path: Path) -> None:
    """Same-entry version progression must not skip cells whose prior-version output exists.

    After v1 completes all 4 cells, submitting v2 with the same matrix must
    treat every v2 cell as pending; c*-v1-* directories must not influence
    the v2 resume decision.
    """
    v1_config = _config_with_matrix_versioned(version=1)
    v1_cells = compile_cells(v1_config)
    for cell in v1_cells:
        cell_dir = tmp_path / cell_subdir_name(cell.cell, v1_config.version, take=1)
        cell_dir.mkdir(parents=True)
        (cell_dir / "out.png").write_bytes(b"fake")

    v2_config = _config_with_matrix_versioned(version=2)
    v2_cells = compile_cells(v2_config)
    pending = pending_cells(
        cells=v2_cells, output_dir=tmp_path, version=v2_config.version, take=1
    )

    assert [cell.cell for cell in pending] == [1, 2, 3, 4]


def test_pending_cells_treats_new_take_as_fully_pending(tmp_path: Path) -> None:
    """Same-version take progression must materialize a new cell folder group."""
    config = _config_with_matrix_versioned(version=1)
    cells = compile_cells(config)
    for cell in cells:
        cell_dir = tmp_path / cell_subdir_name(cell.cell, config.version, take=1)
        cell_dir.mkdir(parents=True)
        (cell_dir / "out.png").write_bytes(b"fake")

    pending = pending_cells(
        cells=cells, output_dir=tmp_path, version=config.version, take=2
    )

    assert [cell.cell for cell in pending] == [1, 2, 3, 4]


def test_pending_cells_does_not_touch_prior_version_directories(tmp_path: Path) -> None:
    """v2 submit must materialize new cN-v2-1/ siblings without modifying cN-v1-1/."""
    v1_config = _config_with_matrix_versioned(version=1)
    v1_cells = compile_cells(v1_config)
    for cell in v1_cells:
        cell_dir = tmp_path / cell_subdir_name(cell.cell, v1_config.version, take=1)
        cell_dir.mkdir(parents=True)
        (cell_dir / "out.png").write_bytes(b"fake-v1")

    v2_config = _config_with_matrix_versioned(version=2)
    v2_cells = compile_cells(v2_config)
    for cell in v2_cells:
        write_compiled_child(config=v2_config, cell=cell, output_dir=tmp_path, take=1)

    for cell in v1_cells:
        v1_dir = tmp_path / cell_subdir_name(cell.cell, 1, take=1)
        assert (v1_dir / "out.png").read_bytes() == b"fake-v1"
    for cell in v2_cells:
        v2_dir = tmp_path / cell_subdir_name(cell.cell, 2, take=1)
        assert (v2_dir / f"c{cell.cell}-v2-1-job.yaml").is_file()
