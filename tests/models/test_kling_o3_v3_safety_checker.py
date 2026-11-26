from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import validate_parameters

APP_IDS = [
    *[
        f"fal-ai/kling-video/o3/{tier}/{mode}"
        for tier in ("pro", "4k")
        for mode in ("text-to-video", "image-to-video", "reference-to-video", "video-to-video/edit")
    ],
    "fal-ai/kling-video/o3/4k/video-to-video/reference",
    *[
        f"fal-ai/kling-video/v3/{tier}/{mode}-to-video"
        for tier in ("pro", "4k", "turbo/pro", "turbo/standard")
        for mode in ("text", "image")
    ],
    *[f"fal-ai/kling-video/v3/{tier}/motion-control" for tier in ("pro", "standard")],
]


def minimal_parameters(app_id: str) -> dict[str, object]:
    if app_id.endswith("/motion-control"):
        return {
            "image_url": "https://example.com/character.png",
            "video_url": "https://example.com/motion.mp4",
            "character_orientation": "image",
        }
    parameters: dict[str, object] = {"prompt": "A heron takes flight."}
    if "/video-to-video/" in app_id:
        parameters["video_url"] = "https://example.com/reference.mp4"
    elif app_id.endswith("/image-to-video"):
        key = "start_image_url" if "/v3/" in app_id and "/turbo/" not in app_id else "image_url"
        parameters[key] = "https://example.com/start.png"
    return parameters


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("enabled", [True, False])
def test_kling_o3_v3_accept_safety_checker_setting(app_id: str, enabled: bool) -> None:
    config = validate_parameters(
        app_id, {**minimal_parameters(app_id), "enable_safety_checker": enabled}
    )

    assert config is not None
    assert config.model_dump()["enable_safety_checker"] is enabled


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_o3_v3_default_safety_checker_in_configs_and_job_examples(app_id: str) -> None:
    config = validate_parameters(app_id, minimal_parameters(app_id))
    assert config is not None
    assert config.model_dump()["enable_safety_checker"] is True

    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    job = YAML(typ="safe").load(result.output)
    assert job["version"] == 1
    assert job["app_id"] == app_id
    assert job["parameters"]["enable_safety_checker"] is True
    assert "random_seed_field" not in job["parameters"]


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("invalid", [None, "invalid"])
def test_kling_o3_v3_reject_invalid_safety_checker_setting(app_id: str, invalid: object) -> None:
    with pytest.raises(ValidationError, match="enable_safety_checker"):
        validate_parameters(
            app_id, {**minimal_parameters(app_id), "enable_safety_checker": invalid}
        )
