from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from falx.models import JobConfig, validate_job_schema


def test_validate_job_schema_returns_pure_input_job_config() -> None:
    validated = validate_job_schema(
        {
            "app_id": "fal-ai/flux/schnell",
            "parameters": {"prompt": "a cat"},
            "output_dir": "workspace/experiments/01-falx_demo/output",
            "slug": "demo-cat",
            "version": 2,
            "iterations": 3,
        }
    )

    assert validated == JobConfig(
        app_id="fal-ai/flux/schnell",
        parameters={"prompt": "a cat"},
        output_dir="workspace/experiments/01-falx_demo/output",
        slug="demo-cat",
        version=2,
        iterations=3,
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "app_id": "fal-ai/flux/schnell",
            "parameters": {"prompt": "a cat"},
            "results": [
                {
                    "request_id": "req-123",
                    "submitted_at": "2026-04-19T14:30:22+09:00",
                }
            ],
        },
        {
            "app_id": "fal-ai/flux/schnell",
            "parameters": {"prompt": "a cat"},
            "request_id": "req-123",
            "submitted_at": "2026-04-19T14:30:22+09:00",
            "result": {"images": [{"url": "https://fal.media/files/cat.png"}]},
        },
    ],
)
def test_validate_job_schema_rejects_stored_result_state(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        validate_job_schema(payload)


def test_validate_job_schema_rejects_non_positive_iterations() -> None:
    with pytest.raises(ValidationError):
        validate_job_schema(
            {
                "app_id": "fal-ai/flux/schnell",
                "parameters": {"prompt": "a cat"},
                "iterations": 0,
            }
        )


def test_validate_job_schema_rejects_missing_slug() -> None:
    with pytest.raises(ValidationError):
        validate_job_schema(
            {
                "app_id": "fal-ai/flux/schnell",
                "parameters": {"prompt": "a cat"},
                "version": 1,
            }
        )


def test_validate_job_schema_rejects_missing_version() -> None:
    with pytest.raises(ValidationError):
        validate_job_schema(
            {
                "app_id": "fal-ai/flux/schnell",
                "parameters": {"prompt": "a cat"},
                "slug": "demo-cat",
            }
        )


def test_job_config_is_frozen_and_forbids_extra_fields() -> None:
    assert JobConfig.model_config.get("frozen") is True
    assert JobConfig.model_config.get("extra") == "forbid"

    with pytest.raises(ValidationError):
        JobConfig(
            app_id="fal-ai/flux/schnell",
            parameters={"prompt": "a cat"},
            slug="demo-cat",
            version=1,
            unexpected=True,
        )


def test_job_config_max_concurrency_defaults_to_eight() -> None:
    config = JobConfig(
        app_id="fal-ai/flux/schnell",
        parameters={"prompt": "a cat"},
        slug="demo-cat",
        version=1,
    )

    assert config.max_concurrency == 8


def test_job_config_max_concurrency_accepts_explicit_override() -> None:
    config = JobConfig(
        app_id="fal-ai/flux/schnell",
        parameters={"prompt": "a cat"},
        slug="demo-cat",
        version=1,
        max_concurrency=4,
    )

    assert config.max_concurrency == 4


def test_job_config_max_concurrency_rejects_zero_and_negative() -> None:
    with pytest.raises(ValidationError):
        JobConfig(
            app_id="fal-ai/flux/schnell",
            parameters={"prompt": "a cat"},
            slug="demo-cat",
            version=1,
            max_concurrency=0,
        )
    with pytest.raises(ValidationError):
        JobConfig(
            app_id="fal-ai/flux/schnell",
            parameters={"prompt": "a cat"},
            slug="demo-cat",
            version=1,
            max_concurrency=-1,
        )


def test_validate_job_schema_round_trips_max_concurrency() -> None:
    validated = validate_job_schema(
        {
            "app_id": "fal-ai/flux/schnell",
            "parameters": {"prompt": "a cat"},
            "slug": "demo-cat",
            "version": 1,
            "max_concurrency": 16,
        }
    )

    assert validated.max_concurrency == 16


def test_job_config_model_dump_json_serializes_path_like_output_dir() -> None:
    config = JobConfig(
        app_id="fal-ai/flux/schnell",
        parameters={"prompt": "a cat"},
        output_dir=Path("workspace/experiments/01-falx_demo/output"),
        slug="demo-cat",
        version=1,
    )

    assert config.output_dir == "workspace/experiments/01-falx_demo/output"
    assert (
        config.model_dump(mode="json", exclude_none=True)["output_dir"]
        == "workspace/experiments/01-falx_demo/output"
    )
