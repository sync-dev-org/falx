from __future__ import annotations

from typing import Literal

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig


class ExampleConfig(BaseFalConfig):
    app_id: Literal["example/app"]
    prompt: str


def test_base_fal_config_forbids_extra_fields() -> None:
    assert BaseFalConfig.model_config.get("extra") == "forbid"

    with pytest.raises(ValidationError):
        ExampleConfig(app_id="example/app", prompt="a cat", unexpected=True)
