from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from falx.io import load_job_config, load_job_config_for_submit, resolve_output_dir
from falx.models import JobConfig
from tests.yaml_utils import safe_dump


def test_load_job_config_reads_pure_input_spec(tmp_path: Path) -> None:
    config_path = tmp_path / "job.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/flux/schnell",
                "parameters": {"prompt": "a cat"},
                "output_dir": "workspace/experiments/01-falx_demo/output",
                "slug": "demo-cat",
                "version": 2,
                "iterations": 3,
            },
            sort_keys=False,
        )
    )

    config = load_job_config(config_path)

    assert config == JobConfig(
        app_id="fal-ai/flux/schnell",
        parameters={"prompt": "a cat"},
        output_dir="workspace/experiments/01-falx_demo/output",
        slug="demo-cat",
        version=2,
        iterations=3,
    )


def test_load_job_config_defaults_iterations(copy_fixture: callable) -> None:
    config = load_job_config(copy_fixture("minimal.yaml"))

    assert config == JobConfig(
        app_id="fal-ai/flux/schnell",
        parameters={"prompt": "a cat sitting on a mat", "num_images": 2},
        iterations=1,
        version=1,
        slug="minimal-cat",
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "app_id": "fal-ai/flux/schnell",
            "parameters": {"prompt": "a cat"},
            "results": [{"request_id": "req-123", "submitted_at": "2026-04-19T14:30:22+09:00"}],
        },
        {
            "app_id": "fal-ai/flux/schnell",
            "request_id": "abc12345-6789-4def-abcd-ef0123456789",
            "submitted_at": "2026-04-19T14:30:22+09:00",
            "parameters": {"prompt": "a cat"},
        },
    ],
)
def test_load_job_config_rejects_stored_result_state(
    tmp_path: Path,
    payload: dict[str, object],
) -> None:
    config_path = tmp_path / "submitted.yaml"
    config_path.write_text(safe_dump(payload, sort_keys=False))

    with pytest.raises(ValidationError):
        load_job_config(config_path)


def test_load_job_config_for_submit_has_same_pure_input_contract(tmp_path: Path) -> None:
    config_path = tmp_path / "job.yaml"
    config_path.write_text(
        safe_dump(
            {
                "app_id": "fal-ai/flux/schnell",
                "parameters": {"prompt": "a cat"},
                "iterations": 2,
                "results": [{"request_id": "req-123", "submitted_at": "2026-04-19T14:30:22+09:00"}],
            },
            sort_keys=False,
        )
    )

    with pytest.raises(ValidationError):
        load_job_config_for_submit(config_path)


def test_resolve_output_dir_preserves_project_relative_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FALX_OUTPUT_DIR", raising=False)

    assert resolve_output_dir(
        None,
        "workspace/experiments/01-falx_demo/output",
    ) == Path("workspace/experiments/01-falx_demo/output")


def test_resolve_output_dir_precedence_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FALX_OUTPUT_DIR", "workspace/from-env")

    assert resolve_output_dir(
        Path("workspace/from-cli"),
        "workspace/from-config",
    ) == Path("workspace/from-cli")
    assert resolve_output_dir(None, "workspace/from-config") == Path("workspace/from-config")
    assert resolve_output_dir(None, None) == Path("workspace/from-env")
