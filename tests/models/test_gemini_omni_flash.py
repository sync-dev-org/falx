from __future__ import annotations

from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx import models
from falx.cli import app

_ROOT = "google/gemini-omni-flash"
_PROMPT = "A lighthouse beam sweeps across the sea."
_IMAGE = "https://example.com/start.png"
_VIDEO = "https://example.com/input.mp4"
_CASES: dict[str, tuple[str, dict[str, Any], dict[str, Any]]] = {
    _ROOT: (
        "GeminiOmniFlashTextToVideoConfig",
        {"prompt": _PROMPT},
        {"aspect_ratio": "16:9", "duration": 8, "enable_safety_checker": True},
    ),
    f"{_ROOT}/edit": (
        "GeminiOmniFlashEditConfig",
        {"prompt": _PROMPT, "video_url": _VIDEO},
        {},
    ),
    f"{_ROOT}/image-to-video": (
        "GeminiOmniFlashImageToVideoConfig",
        {"prompt": _PROMPT, "image_url": _IMAGE},
        {"aspect_ratio": "16:9", "duration": 8},
    ),
    f"{_ROOT}/reference-to-video": (
        "GeminiOmniFlashReferenceToVideoConfig",
        {"prompt": _PROMPT, "image_urls": [_IMAGE]},
        {"aspect_ratio": "16:9", "duration": 8},
    ),
    f"{_ROOT}/v1.2/text-to-video": (
        "GeminiOmniFlashV12TextToVideoConfig",
        {"prompt": _PROMPT},
        {"aspect_ratio": "16:9", "resolution": "720p", "duration": 8},
    ),
    f"{_ROOT}/v1.2/image-to-video": (
        "GeminiOmniFlashV12ImageToVideoConfig",
        {"prompt": _PROMPT, "image_url": _IMAGE},
        {"end_image_url": None, "aspect_ratio": "16:9", "resolution": "720p", "duration": 8},
    ),
    f"{_ROOT}/v1.2/reference-to-video": (
        "GeminiOmniFlashV12ReferenceToVideoConfig",
        {"prompt": _PROMPT},
        {
            "image_urls": None,
            "reference_video_urls": None,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "duration": 8,
        },
    ),
    f"{_ROOT}/v1.2/edit": (
        "GeminiOmniFlashV12EditConfig",
        {"prompt": _PROMPT, "video_url": _VIDEO},
        {"resolution": "720p"},
    ),
    f"{_ROOT}/v1.2/extend": (
        "GeminiOmniFlashV12ExtendConfig",
        {"prompt": _PROMPT, "video_url": _VIDEO},
        {"resolution": "720p", "duration": 8},
    ),
    f"{_ROOT}/v1.2/upscale": (
        "GeminiOmniFlashV12UpscaleConfig",
        {"video_url": _VIDEO},
        {"resolution": "1080p"},
    ),
}
_DURATION_LIMITS = {
    _ROOT: 10,
    f"{_ROOT}/image-to-video": 10,
    f"{_ROOT}/reference-to-video": 10,
    f"{_ROOT}/v1.2/text-to-video": 15,
    f"{_ROOT}/v1.2/image-to-video": 15,
    f"{_ROOT}/v1.2/reference-to-video": 15,
    f"{_ROOT}/v1.2/extend": 10,
}
_ENUMS = {
    (app_id, field): values
    for app_id, (_, _, defaults) in _CASES.items()
    for field, values in (
        ("aspect_ratio", ("16:9", "9:16")),
        (
            "resolution",
            ("720p", "1080p", "4k")
            if app_id.endswith("/upscale")
            else ("360p", "720p", "1080p", "4k"),
        ),
    )
    if field in defaults
}


def _config(app_id: str, **parameters: Any) -> models.BaseFalConfig:
    config_class = models.config_class_for_app_id(app_id)
    assert config_class is not None, f"Missing config for {app_id}"
    return config_class.model_validate({"app_id": app_id, **_CASES[app_id][1], **parameters})


@pytest.mark.parametrize("app_id", _CASES)
def test_omni_endpoints_are_registered_with_defaults_and_without_seed(app_id: str) -> None:
    class_name, required, defaults = _CASES[app_id]
    config = _config(app_id)

    assert app_id in models.SUPPORTED_APP_IDS
    assert type(config) is getattr(models, class_name)
    assert config.random_seed_field is None
    assert config.model_dump() == {"app_id": app_id, **required, **defaults}
    parsed = TypeAdapter(models.FalConfig).validate_python({"app_id": app_id, **required})
    assert type(parsed) is type(config)
    assert models.validate_parameters(app_id, required) == config


@pytest.mark.parametrize(
    ("app_id", "field"),
    [(app_id, field) for app_id, (_, required, _) in _CASES.items() for field in required],
)
def test_omni_endpoints_reject_missing_required_inputs(app_id: str, field: str) -> None:
    config_class = models.config_class_for_app_id(app_id)
    assert config_class is not None
    payload = {"app_id": app_id, **_CASES[app_id][1]}
    del payload[field]

    with pytest.raises(ValidationError, match=field):
        config_class.model_validate(payload)


@pytest.mark.parametrize(
    "app_id", [key for key, (_, fields, _) in _CASES.items() if "prompt" in fields]
)
def test_omni_prompt_length_matches_api_limit(app_id: str) -> None:
    assert _config(app_id, prompt="x" * 20_000).prompt == "x" * 20_000

    with pytest.raises(ValidationError, match="prompt"):
        _config(app_id, prompt="x" * 20_001)


@pytest.mark.parametrize(("app_id", "maximum"), _DURATION_LIMITS.items())
def test_omni_video_duration_accepts_api_boundaries(app_id: str, maximum: int) -> None:
    for duration in (3, maximum):
        assert _config(app_id, duration=duration).duration == duration


@pytest.mark.parametrize(("app_id", "maximum"), _DURATION_LIMITS.items())
def test_omni_video_duration_rejects_values_outside_api_range(app_id: str, maximum: int) -> None:
    for duration in (2, maximum + 1):
        with pytest.raises(ValidationError, match="duration"):
            _config(app_id, duration=duration)


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [(app_id, field, value) for (app_id, field), values in _ENUMS.items() for value in values],
)
def test_omni_accepts_api_aspect_ratios_and_resolutions(
    app_id: str, field: str, value: str
) -> None:
    assert getattr(_config(app_id, **{field: value}), field) == value


@pytest.mark.parametrize(("app_id", "field"), _ENUMS)
def test_omni_rejects_values_outside_api_enums(app_id: str, field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        _config(app_id, **{field: "unsupported"})


@pytest.mark.parametrize("count", (1, 10))
def test_unversioned_reference_video_accepts_api_image_counts(count: int) -> None:
    assert (
        len(_config(f"{_ROOT}/reference-to-video", image_urls=[_IMAGE] * count).image_urls) == count
    )


@pytest.mark.parametrize("images", (None, [], [_IMAGE] * 11))
def test_unversioned_reference_video_requires_one_to_ten_images(images: Any) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        _config(f"{_ROOT}/reference-to-video", image_urls=images)


@pytest.mark.parametrize(("field", "maximum"), (("image_urls", 10), ("reference_video_urls", 3)))
def test_v12_reference_media_counts_match_api_limits(field: str, maximum: int) -> None:
    app_id = f"{_ROOT}/v1.2/reference-to-video"
    for count in (0, maximum):
        assert len(getattr(_config(app_id, **{field: [_IMAGE] * count}), field)) == count

    with pytest.raises(ValidationError, match=field):
        _config(app_id, **{field: [_IMAGE] * (maximum + 1)})


@pytest.mark.parametrize("duration", (3, 10))
def test_v12_interpolation_accepts_up_to_ten_seconds(duration: int) -> None:
    config = _config(f"{_ROOT}/v1.2/image-to-video", duration=duration, end_image_url=_IMAGE)
    assert config.duration == duration
    assert config.end_image_url == _IMAGE


@pytest.mark.parametrize("duration", (11, 15))
def test_v12_interpolation_rejects_more_than_ten_seconds(duration: int) -> None:
    with pytest.raises(ValidationError, match="duration"):
        _config(f"{_ROOT}/v1.2/image-to-video", duration=duration, end_image_url=_IMAGE)


def test_unversioned_text_to_video_can_disable_safety_checker() -> None:
    assert _config(_ROOT, enable_safety_checker=False).enable_safety_checker is False


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [(app_id, "seed", 42) for app_id in _CASES]
    + [(app_id, "resolution", "720p") for app_id in _CASES if "/v1.2/" not in app_id]
    + [
        (f"{_ROOT}/edit", "duration", 8),
        (f"{_ROOT}/edit", "aspect_ratio", "16:9"),
        (f"{_ROOT}/image-to-video", "end_image_url", _IMAGE),
        (f"{_ROOT}/reference-to-video", "reference_video_urls", [_VIDEO]),
        (f"{_ROOT}/v1.2/edit", "duration", 8),
        (f"{_ROOT}/v1.2/edit", "aspect_ratio", "16:9"),
        (f"{_ROOT}/v1.2/extend", "aspect_ratio", "16:9"),
        (f"{_ROOT}/v1.2/upscale", "prompt", _PROMPT),
        (f"{_ROOT}/v1.2/upscale", "duration", 8),
        (f"{_ROOT}/v1.2/upscale", "resolution", "360p"),
    ],
)
def test_omni_endpoints_reject_fields_and_values_from_other_routes(
    app_id: str, field: str, value: Any
) -> None:
    with pytest.raises(ValidationError, match=field):
        _config(app_id, **{field: value})


def test_models_command_lists_all_added_omni_endpoints() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert _CASES.keys() <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", _CASES)
def test_omni_schema_command_emits_valid_job_examples(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    payload = YAML(typ="safe").load(result.stdout)
    job = models.JobConfig.model_validate(payload)
    assert job.app_id == app_id
    assert job.parameters.keys() == (_CASES[app_id][1].keys() | _CASES[app_id][2].keys())
    assert models.validate_parameters(app_id, job.parameters) is not None
