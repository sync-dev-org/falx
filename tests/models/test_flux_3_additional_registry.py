from __future__ import annotations

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

import falx.models as models
from falx.cli import app

PREFIX = "blackforestlabs/flux-3/"
ROUTE_CLASSES = {
    "text-to-video/draft": "Flux3TextToVideoDraftConfig",
    "image-to-video/draft": "Flux3ImageToVideoDraftConfig",
    "first-last-frame-to-video/draft": "Flux3FirstLastFrameToVideoDraftConfig",
    "keyframes-to-video/draft": "Flux3KeyframesToVideoDraftConfig",
    "extend-video/draft": "Flux3ExtendVideoDraftConfig",
    "draft-enhance": "Flux3DraftEnhanceConfig",
    "text-to-image": "Flux3TextToImageConfig",
    "edit-image": "Flux3EditImageConfig",
    "klein/text-to-image": "Flux3KleinTextToImageConfig",
    "klein/edit-image": "Flux3KleinEditImageConfig",
    "klein/text-to-image/lora": "Flux3KleinTextToImageLoraConfig",
    "klein/edit-image/lora": "Flux3KleinEditImageLoraConfig",
    "klein/base/text-to-image/lora": "Flux3KleinBaseTextToImageLoraConfig",
    "klein/base/edit-image/lora": "Flux3KleinBaseEditImageLoraConfig",
}
runner = CliRunner()


@pytest.mark.parametrize(("route", "class_name"), ROUTE_CLASSES.items())
def test_additional_routes_are_registered_and_exported(route: str, class_name: str) -> None:
    app_id = PREFIX + route
    assert app_id in models.SUPPORTED_APP_IDS
    config_class = models.config_class_for_app_id(app_id)
    assert config_class is getattr(models, class_name)
    assert class_name in models.__all__
    assert config_class.random_seed_field == ("seed" if route.startswith("klein/") else None)


def test_models_lists_all_additional_flux_routes() -> None:
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert {PREFIX + route for route in ROUTE_CLASSES} <= set(result.stdout.splitlines())


@pytest.mark.parametrize("route", ROUTE_CLASSES)
def test_schema_examples_validate_for_all_additional_flux_routes(route: str) -> None:
    app_id = PREFIX + route
    result = runner.invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    example = YAML(typ="safe").load(result.stdout)
    assert example["app_id"] == app_id
    job = models.validate_job_schema(example)
    config = models.validate_parameters(job.app_id, job.parameters)
    assert config is not None
    assert set(example["parameters"]) == set(type(config).model_fields) - {"app_id"}
