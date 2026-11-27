from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import SUPPORTED_APP_IDS, config_class_for_app_id, validate_parameters

APP_IDS = {
    "fal-ai/marigold-v2": "MarigoldV2Config",
    "fal-ai/moss-image": "MossImageConfig",
    "recraft/v4.1/flash/v2/text-to-image": "RecraftV41FlashV2TextToImageConfig",
    "recraft/vectorize/pro": "RecraftVectorizeProConfig",
}

runner = CliRunner()
safe_yaml = YAML(typ="safe")


@pytest.mark.parametrize("app_id", APP_IDS)
def test_marigold_moss_and_recraft_are_registered_with_seed_metadata(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class.__name__ == APP_IDS[app_id]
    assert config_class.random_seed_field == ("seed" if app_id.startswith("fal-ai/") else None)


def test_models_lists_marigold_moss_and_recraft() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert APP_IDS.keys() <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_examples_validate_for_marigold_moss_and_recraft(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    config = validate_parameters(app_id, payload["parameters"])
    assert config is not None
    assert config.__class__.__name__ == APP_IDS[app_id]
