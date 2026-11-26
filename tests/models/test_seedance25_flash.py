from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    BaseFalConfig,
    config_class_for_app_id,
    validate_parameters,
)

TEXT_APP_ID = "bytedance/seedance-2.5/flash/text-to-video"
IMAGE_APP_ID = "bytedance/seedance-2.5/flash/image-to-video"
REFERENCE_APP_ID = "bytedance/seedance-2.5/flash/reference-to-video"
APP_IDS = [TEXT_APP_ID, IMAGE_APP_ID, REFERENCE_APP_ID]
MINIMAL_PARAMETERS = {
    TEXT_APP_ID: {"prompt": "A continuous tracking shot through a lantern-lit market."},
    IMAGE_APP_ID: {"image_url": "https://example.com/start.png"},
    REFERENCE_APP_ID: {},
}
COMMON_DEFAULTS = {
    "resolution": "720p",
    "duration": "auto",
    "aspect_ratio": "auto",
    "generate_audio": True,
    "bitrate_mode": "standard",
    "codec": "auto",
    "output_format": "mp4",
    "return_last_frame": False,
    "end_user_id": None,
}
runner = CliRunner()
safe_yaml = YAML(typ="safe")


@pytest.mark.parametrize("app_id", APP_IDS)
def test_flash_endpoints_validate_minimal_inputs_with_documented_defaults(app_id: str) -> None:
    config = validate_parameters(app_id, MINIMAL_PARAMETERS[app_id])

    expected = {"app_id": app_id, **COMMON_DEFAULTS, **MINIMAL_PARAMETERS[app_id]}
    if app_id == IMAGE_APP_ID:
        expected.update(prompt=None, end_image_url=None)
    elif app_id == REFERENCE_APP_ID:
        expected.update(
            prompt=None, task="reference", image_urls=[], video_urls=[], audio_urls=[], seed=None
        )
    assert isinstance(config, BaseFalConfig)
    assert config.model_dump() == expected
    assert (
        config.__class__.__name__
        == {
            TEXT_APP_ID: "Seedance25FlashTextToVideoConfig",
            IMAGE_APP_ID: "Seedance25FlashImageToVideoConfig",
            REFERENCE_APP_ID: "Seedance25FlashReferenceToVideoConfig",
        }[app_id]
    )


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        *(("duration", value) for value in ["auto", *(str(n) for n in range(4, 31))]),
        *(("resolution", value) for value in ["480p", "720p"]),
        *(("bitrate_mode", value) for value in ["standard", "high"]),
        *(("codec", value) for value in ["auto", "H264", "H265"]),
        *(("output_format", value) for value in ["mp4", "mov"]),
        ("generate_audio", False),
        ("return_last_frame", True),
        ("end_user_id", "user-123"),
    ],
)
def test_flash_endpoints_accept_documented_options(app_id: str, field: str, value: object) -> None:
    config = validate_parameters(app_id, {**MINIMAL_PARAMETERS[app_id], field: value})

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()[field] == value


@pytest.mark.parametrize("app_id", [TEXT_APP_ID, REFERENCE_APP_ID])
@pytest.mark.parametrize("aspect_ratio", ["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_flash_text_and_reference_accept_documented_aspect_ratios(
    app_id: str, aspect_ratio: str
) -> None:
    config = validate_parameters(
        app_id, {**MINIMAL_PARAMETERS[app_id], "aspect_ratio": aspect_ratio}
    )

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()["aspect_ratio"] == aspect_ratio


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 4),
        ("duration", "3"),
        ("duration", "31"),
        ("aspect_ratio", "2:1"),
        ("resolution", "1080p"),
        ("resolution", "4k"),
        ("bitrate_mode", "lossless"),
        ("codec", "AV1"),
        ("output_format", "webm"),
        ("unexpected", True),
    ],
)
def test_flash_endpoints_reject_unsupported_options(app_id: str, field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**MINIMAL_PARAMETERS[app_id], field: value})


@pytest.mark.parametrize(
    ("app_id", "field"), [(TEXT_APP_ID, "prompt"), (IMAGE_APP_ID, "image_url")]
)
@pytest.mark.parametrize("parameters", [{}, {"prompt": None, "image_url": None}])
def test_flash_endpoints_reject_missing_or_null_required_inputs(
    app_id: str, field: str, parameters: dict[str, object]
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", [IMAGE_APP_ID, REFERENCE_APP_ID])
@pytest.mark.parametrize("prompt", [None, "", "A slow camera orbit around the subject."])
def test_flash_image_and_reference_accept_nullable_optional_prompts(
    app_id: str, prompt: str | None
) -> None:
    config = validate_parameters(app_id, {**MINIMAL_PARAMETERS[app_id], "prompt": prompt})

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()["prompt"] == prompt


def test_flash_image_accepts_end_frame_and_requires_auto_aspect_ratio() -> None:
    config = validate_parameters(
        IMAGE_APP_ID,
        {**MINIMAL_PARAMETERS[IMAGE_APP_ID], "end_image_url": "https://example.com/end.png"},
    )

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()["end_image_url"] == "https://example.com/end.png"
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validate_parameters(
            IMAGE_APP_ID, {**MINIMAL_PARAMETERS[IMAGE_APP_ID], "aspect_ratio": "16:9"}
        )


@pytest.mark.parametrize("task", ["auto", "reference", "editing", "extension"])
def test_flash_reference_accepts_documented_tasks(task: str) -> None:
    config = validate_parameters(
        REFERENCE_APP_ID,
        {"task": task, "video_urls": ["https://example.com/reference.mov"]},
    )

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()["task"] == task


def test_flash_reference_rejects_unsupported_tasks() -> None:
    with pytest.raises(ValidationError, match="task"):
        validate_parameters(REFERENCE_APP_ID, {"task": "interpolation"})


@pytest.mark.parametrize(
    ("field", "limit"), [("image_urls", 10), ("video_urls", 5), ("audio_urls", 5)]
)
def test_flash_reference_enforces_each_documented_media_limit(field: str, limit: int) -> None:
    urls = [f"https://example.com/reference-{n}" for n in range(limit)]
    config = validate_parameters(REFERENCE_APP_ID, {field: urls})

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()[field] == urls
    with pytest.raises(ValidationError, match=field):
        validate_parameters(REFERENCE_APP_ID, {field: [*urls, "https://example.com/extra"]})


@pytest.mark.parametrize("field", ["image_urls", "video_urls", "audio_urls"])
@pytest.mark.parametrize("value", [None, [42]])
def test_flash_reference_rejects_null_lists_and_non_string_media(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(REFERENCE_APP_ID, {field: value})


@pytest.mark.parametrize("seed", [None, -1, 42, 2**40])
def test_flash_reference_accepts_nullable_integer_seed(seed: int | None) -> None:
    config = validate_parameters(REFERENCE_APP_ID, {"seed": seed})

    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()["seed"] == seed


@pytest.mark.parametrize("app_id", [TEXT_APP_ID, IMAGE_APP_ID])
def test_flash_text_and_image_reject_seed_input(app_id: str) -> None:
    with pytest.raises(ValidationError, match="seed"):
        validate_parameters(app_id, {**MINIMAL_PARAMETERS[app_id], "seed": 42})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_flash_schema_produces_valid_job_yaml_and_models_lists_endpoint(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    config = validate_parameters(app_id, payload["parameters"])
    assert isinstance(config, BaseFalConfig)
    assert config.model_dump()["resolution"] == "720p"
    assert config.model_dump()["output_format"] == "mp4"
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class.random_seed_field == ("seed" if app_id == REFERENCE_APP_ID else None)

    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert app_id in result.stdout.splitlines()
