from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

import falx.models as models
from falx.cli import app

SEEDANCE2_APP_IDS = tuple(
    f"bytedance/seedance-2.0/us/{mode}-to-video" for mode in ("text", "image", "reference")
)
SEEDANCE25_APP_IDS = tuple(
    f"bytedance/seedance-2.5/us/{mode}-to-video" for mode in ("text", "image", "reference")
)
GENERATION_APP_IDS = SEEDANCE2_APP_IDS + SEEDANCE25_APP_IDS
DRAFT_APP_ID = "bytedance/seedance-2.5/us/draft/complete"
APP_IDS = (*GENERATION_APP_IDS, DRAFT_APP_ID)
REFERENCE_APP_IDS = (SEEDANCE2_APP_IDS[2], SEEDANCE25_APP_IDS[2])
runner = CliRunner()
safe_yaml = YAML(typ="safe")


def minimal_parameters(app_id: str) -> dict[str, object]:
    if app_id == DRAFT_APP_ID:
        return {"draft_id": "draft-from-preview"}
    if app_id == SEEDANCE25_APP_IDS[2]:
        return {}
    if app_id == SEEDANCE25_APP_IDS[1]:
        return {"image_url": "https://example.com/start.png"}
    parameters: dict[str, object] = {"prompt": "A crane flies over a lake."}
    if app_id == SEEDANCE2_APP_IDS[1]:
        parameters["image_url"] = "https://example.com/start.png"
    return parameters


def expected_defaults(app_id: str) -> dict[str, object]:
    if app_id == DRAFT_APP_ID:
        return {"resolution": "1080p", "codec": "auto", "output_format": "mp4"}
    defaults: dict[str, object] = {
        "resolution": "720p",
        "duration": "auto",
        "aspect_ratio": "auto",
        "generate_audio": True,
        "bitrate_mode": "standard",
        "codec": "auto",
        "return_last_frame": False,
        "end_user_id": None,
    }
    if app_id in SEEDANCE25_APP_IDS:
        defaults.update(draft=False, output_format="mp4")
    if app_id.endswith("/image-to-video"):
        defaults["end_image_url"] = None
    if app_id in (SEEDANCE25_APP_IDS[1], SEEDANCE25_APP_IDS[2]):
        defaults["prompt"] = None
    if app_id in REFERENCE_APP_IDS:
        defaults.update(image_urls=[], video_urls=[], audio_urls=[])
    if app_id == SEEDANCE25_APP_IDS[2]:
        defaults.update(task="reference", seed=None)
    return defaults


@pytest.mark.parametrize(
    ("app_id", "class_name"),
    [
        (SEEDANCE2_APP_IDS[0], "Seedance2UsTextToVideoConfig"),
        (SEEDANCE2_APP_IDS[1], "Seedance2UsImageToVideoConfig"),
        (SEEDANCE2_APP_IDS[2], "Seedance2UsReferenceToVideoConfig"),
        (SEEDANCE25_APP_IDS[0], "Seedance25UsTextToVideoConfig"),
        (SEEDANCE25_APP_IDS[1], "Seedance25UsImageToVideoConfig"),
        (SEEDANCE25_APP_IDS[2], "Seedance25UsReferenceToVideoConfig"),
        (DRAFT_APP_ID, "Seedance25UsDraftCompleteConfig"),
    ],
)
def test_seedance_us_parameters_route_to_exported_model(app_id: str, class_name: str) -> None:
    assert app_id in models.SUPPORTED_APP_IDS
    config_class = models.config_class_for_app_id(app_id)
    assert config_class is getattr(models, class_name)
    adapter = TypeAdapter(models.FalConfig)
    parsed = adapter.validate_python({"app_id": app_id, **minimal_parameters(app_id)})
    assert type(parsed) is config_class
    assert config_class.random_seed_field == ("seed" if app_id == SEEDANCE25_APP_IDS[2] else None)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_seedance_us_accepts_documented_defaults(app_id: str) -> None:
    parameters = minimal_parameters(app_id)
    config = models.validate_parameters(app_id, parameters)

    assert config.model_dump() == {"app_id": app_id, **expected_defaults(app_id), **parameters}


@pytest.mark.parametrize("app_id", GENERATION_APP_IDS)
def test_seedance_us_preserves_output_and_user_options(app_id: str) -> None:
    parameters = {
        **minimal_parameters(app_id),
        "codec": "H265",
        "return_last_frame": True,
        "generate_audio": False,
        "bitrate_mode": "high",
        "resolution": "4k",
        "end_user_id": "end-user-123",
    }
    if app_id in SEEDANCE25_APP_IDS:
        parameters.update(draft=True, output_format="mov")
    if app_id.endswith("/image-to-video"):
        parameters["end_image_url"] = "https://example.com/end.png"

    config = models.validate_parameters(app_id, parameters)

    assert config.model_dump().items() >= parameters.items()


@pytest.mark.parametrize(
    ("app_id", "duration"),
    [
        (app_id, duration)
        for app_ids, maximum in ((SEEDANCE2_APP_IDS, 15), (SEEDANCE25_APP_IDS, 30))
        for app_id in app_ids
        for duration in ("auto", *(str(value) for value in range(4, maximum + 1)))
    ],
)
def test_seedance_us_accepts_duration_strings(app_id: str, duration: str) -> None:
    config = models.validate_parameters(
        app_id, {**minimal_parameters(app_id), "duration": duration}
    )

    assert config.model_dump()["duration"] == duration


@pytest.mark.parametrize("app_id", GENERATION_APP_IDS)
@pytest.mark.parametrize("resolution", ["480p", "720p", "1080p", "4k"])
def test_seedance_us_accepts_generation_resolutions(app_id: str, resolution: str) -> None:
    config = models.validate_parameters(
        app_id, {**minimal_parameters(app_id), "resolution": resolution}
    )

    assert config.model_dump()["resolution"] == resolution


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("codec", ["auto", "H264", "H265"])
def test_seedance_us_accepts_codecs(app_id: str, codec: str) -> None:
    config = models.validate_parameters(app_id, {**minimal_parameters(app_id), "codec": codec})

    assert config.model_dump()["codec"] == codec


@pytest.mark.parametrize(
    "app_id", [app_id for app_id in GENERATION_APP_IDS if app_id != SEEDANCE25_APP_IDS[1]]
)
@pytest.mark.parametrize("aspect_ratio", ["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
def test_seedance_us_accepts_aspect_ratios(app_id: str, aspect_ratio: str) -> None:
    config = models.validate_parameters(
        app_id, {**minimal_parameters(app_id), "aspect_ratio": aspect_ratio}
    )

    assert config.model_dump()["aspect_ratio"] == aspect_ratio


@pytest.mark.parametrize("app_id", GENERATION_APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 4),
        ("duration", "3"),
        ("duration", "31"),
        ("duration", None),
        ("resolution", "2160p"),
        ("aspect_ratio", "2:1"),
        ("bitrate_mode", "lossless"),
        ("codec", "h264"),
        ("return_last_frame", None),
        ("generate_audio", None),
        ("unknown_parameter", True),
    ],
)
def test_seedance_us_rejects_invalid_generation_parameters(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        models.validate_parameters(app_id, {**minimal_parameters(app_id), field: value})


@pytest.mark.parametrize("app_id", SEEDANCE2_APP_IDS)
def test_seedance2_us_rejects_duration_past_fifteen_seconds(app_id: str) -> None:
    with pytest.raises(ValidationError, match="duration"):
        models.validate_parameters(app_id, {**minimal_parameters(app_id), "duration": "16"})


@pytest.mark.parametrize(
    ("app_id", "field"),
    [
        (SEEDANCE2_APP_IDS[0], "prompt"),
        (SEEDANCE2_APP_IDS[1], "prompt"),
        (SEEDANCE2_APP_IDS[1], "image_url"),
        (SEEDANCE2_APP_IDS[2], "prompt"),
        (SEEDANCE25_APP_IDS[0], "prompt"),
        (SEEDANCE25_APP_IDS[1], "image_url"),
        (DRAFT_APP_ID, "draft_id"),
    ],
)
@pytest.mark.parametrize("missing", [True, False], ids=["omitted", "null"])
def test_seedance_us_requires_non_nullable_inputs(app_id: str, field: str, missing: bool) -> None:
    parameters = minimal_parameters(app_id)
    if missing:
        del parameters[field]
    else:
        parameters[field] = None

    with pytest.raises(ValidationError, match=field):
        models.validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", [SEEDANCE25_APP_IDS[1], SEEDANCE25_APP_IDS[2]])
@pytest.mark.parametrize("prompt", [None, "A subject looks toward the camera."])
def test_seedance25_us_accepts_optional_prompt(app_id: str, prompt: str | None) -> None:
    config = models.validate_parameters(app_id, {**minimal_parameters(app_id), "prompt": prompt})

    assert config.model_dump()["prompt"] == prompt


@pytest.mark.parametrize(
    "app_id", [app_id for app_id in APP_IDS if app_id != SEEDANCE25_APP_IDS[2]]
)
def test_seedance_us_rejects_seed_when_api_does_not_accept_seed(app_id: str) -> None:
    with pytest.raises(ValidationError, match="seed"):
        models.validate_parameters(app_id, {**minimal_parameters(app_id), "seed": 42})


def test_seedance25_us_image_to_video_requires_auto_aspect_ratio() -> None:
    app_id = SEEDANCE25_APP_IDS[1]
    with pytest.raises(ValidationError, match="aspect_ratio"):
        models.validate_parameters(app_id, {**minimal_parameters(app_id), "aspect_ratio": "16:9"})


@pytest.mark.parametrize(
    ("app_id", "field", "limit"),
    [
        (app_id, field, limit)
        for app_id, limits in zip(REFERENCE_APP_IDS, [(9, 3, 3), (30, 10, 10)], strict=True)
        for field, limit in zip(("image_urls", "video_urls", "audio_urls"), limits, strict=True)
    ],
)
def test_seedance_us_enforces_reference_file_limits(app_id: str, field: str, limit: int) -> None:
    parameters = {**minimal_parameters(app_id), "image_urls": ["https://example.com/image.png"]}
    urls = [f"https://example.com/ref-{index}" for index in range(limit)]
    config = models.validate_parameters(app_id, {**parameters, field: urls})
    assert config.model_dump()[field] == urls

    with pytest.raises(ValidationError, match=field):
        models.validate_parameters(
            app_id, {**parameters, field: [*urls, "https://example.com/extra"]}
        )


@pytest.mark.parametrize("app_id", REFERENCE_APP_IDS)
@pytest.mark.parametrize("field", ["image_urls", "video_urls", "audio_urls"])
@pytest.mark.parametrize("value", [None, [123]])
def test_seedance_us_requires_non_nullable_string_reference_arrays(
    app_id: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        models.validate_parameters(app_id, {**minimal_parameters(app_id), field: value})


def test_seedance2_us_enforces_twelve_file_combined_budget() -> None:
    app_id = SEEDANCE2_APP_IDS[2]
    parameters = {
        **minimal_parameters(app_id),
        "image_urls": ["https://example.com/image.png"] * 9,
        "video_urls": ["https://example.com/video.mp4"] * 2,
        "audio_urls": ["https://example.com/audio.wav"],
    }
    config = models.validate_parameters(app_id, parameters)
    assert (
        sum(len(config.model_dump()[field]) for field in ("image_urls", "video_urls", "audio_urls"))
        == 12
    )

    parameters["audio_urls"] = ["https://example.com/audio.wav"] * 2
    with pytest.raises(ValidationError, match="total files"):
        models.validate_parameters(app_id, parameters)


def test_seedance2_us_audio_requires_visual_reference() -> None:
    app_id = SEEDANCE2_APP_IDS[2]
    with pytest.raises(ValidationError, match="audio_urls require image_urls or video_urls"):
        models.validate_parameters(
            app_id, {**minimal_parameters(app_id), "audio_urls": ["https://example.com/audio.wav"]}
        )


def test_seedance25_us_accepts_fifty_reference_files() -> None:
    config = models.validate_parameters(
        SEEDANCE25_APP_IDS[2],
        {
            "image_urls": ["https://example.com/image.png"] * 30,
            "video_urls": ["https://example.com/video.mp4"] * 10,
            "audio_urls": ["https://example.com/audio.wav"] * 10,
        },
    )

    assert (
        sum(len(config.model_dump()[field]) for field in ("image_urls", "video_urls", "audio_urls"))
        == 50
    )


def test_seedance25_us_does_not_require_visual_reference_for_audio() -> None:
    config = models.validate_parameters(
        SEEDANCE25_APP_IDS[2], {"audio_urls": ["https://example.com/audio.wav"]}
    )

    assert config.model_dump()["audio_urls"] == ["https://example.com/audio.wav"]


@pytest.mark.parametrize("task", ["auto", "reference", "editing", "extension"])
def test_seedance25_us_preserves_task_and_seed(task: str) -> None:
    parameters = {
        "task": task,
        "video_urls": ["https://example.com/input.mp4"],
        "seed": 42,
    }
    config = models.validate_parameters(SEEDANCE25_APP_IDS[2], parameters)

    assert config.model_dump().items() >= parameters.items()


@pytest.mark.parametrize(
    ("field", "value"),
    [("task", "extend"), ("seed", "invalid"), ("draft", None), ("output_format", "webm")],
)
def test_seedance25_us_rejects_invalid_reference_options(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=field):
        models.validate_parameters(SEEDANCE25_APP_IDS[2], {field: value})


@pytest.mark.parametrize("draft_id", ["x", "x" * 8192])
@pytest.mark.parametrize("resolution", ["1080p", "4k"])
@pytest.mark.parametrize("output_format", ["mp4", "mov"])
def test_seedance25_us_completes_draft_with_documented_options(
    draft_id: str, resolution: str, output_format: str
) -> None:
    parameters = {"draft_id": draft_id, "resolution": resolution, "output_format": output_format}
    config = models.validate_parameters(DRAFT_APP_ID, parameters)

    assert config.model_dump().items() >= parameters.items()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("draft_id", ""),
        ("draft_id", "x" * 8193),
        ("resolution", "720p"),
        ("output_format", "webm"),
        ("codec", "AV1"),
        ("prompt", "An unrelated prompt."),
    ],
)
def test_seedance25_us_rejects_invalid_draft_completion_parameters(
    field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        models.validate_parameters(DRAFT_APP_ID, {**minimal_parameters(DRAFT_APP_ID), field: value})


def test_models_command_lists_all_seedance_us_endpoints() -> None:
    result = runner.invoke(app, ["models"])

    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_command_outputs_valid_seedance_us_job_yaml(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    job = models.JobConfig.model_validate(payload)
    assert job.app_id == app_id
    validated = models.validate_parameters(app_id, job.parameters)
    assert validated.model_dump(exclude={"app_id"}) == job.parameters
    assert job.parameters.items() >= expected_defaults(app_id).items()
