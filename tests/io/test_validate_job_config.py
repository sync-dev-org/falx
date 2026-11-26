from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.io import validate_job_config
from falx.models import JobConfig, NanoBanana2Config


def test_validate_job_config_returns_registered_config() -> None:
    validated = validate_job_config(
        JobConfig(
            app_id="fal-ai/nano-banana-2",
            parameters={"prompt": "a cat on a mat"},
            slug="demo-cat",
            version=1,
        )
    )

    assert isinstance(validated, NanoBanana2Config)


def test_validate_job_config_warns_and_returns_none_for_unregistered_app_id() -> None:
    config = JobConfig(
        app_id="fal-ai/not-registered",
        parameters={"prompt": "a cat"},
        slug="demo-cat",
        version=1,
    )

    with pytest.warns(UserWarning, match="fal-ai/not-registered"):
        validated = validate_job_config(config)

    assert validated is None


def test_validate_job_config_propagates_validation_error() -> None:
    config = JobConfig(
        app_id="fal-ai/nano-banana-2",
        parameters={"prompt": "no", "num_images": 5},
        slug="demo-cat",
        version=1,
    )

    with pytest.raises(ValidationError):
        validate_job_config(config)
