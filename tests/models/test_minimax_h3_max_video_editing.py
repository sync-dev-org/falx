from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

EXTEND_IDS = ["minimax/h3-max/extend-video", "minimax/h3-max-turbo/extend-video"]
INSERT_ID = "minimax/h3-max/insert-video"
RECAST_ID = "minimax/h3-max/recast"
RELIGHT_ID = "minimax/h3-max/relight"
REFRAME_ID = "minimax/h3-max/reframe-video"
THREE_D_ID = "minimax/h3-max/3d-to-video"
LIP_SYNC_ID = "minimax/h3-max/lip-sync/image-to-video"

VIDEO = "https://example.com/source.mp4"
IMAGE = "https://example.com/reference.png"
AUDIO = "https://example.com/voice.wav"

REQUIRED_PARAMETERS = {
    **{
        app_id: {"video_url": VIDEO, "prompt": "The camera follows the subject."}
        for app_id in EXTEND_IDS
    },
    INSERT_ID: {"video_url": VIDEO, "start_time": 2.0, "resume_time": 4.0},
    RECAST_ID: {"video_url": VIDEO, "reference_image_urls": [IMAGE]},
    RELIGHT_ID: {"video_url": VIDEO, "reference_image_url": IMAGE},
    REFRAME_ID: {"video_url": VIDEO},
    THREE_D_ID: {"video_url": VIDEO},
    LIP_SYNC_ID: {"image_url": IMAGE, "audio_url": AUDIO},
}

EXPECTED_CLASSES = {
    EXTEND_IDS[0]: "MinimaxH3MaxExtendVideoConfig",
    EXTEND_IDS[1]: "MinimaxH3MaxTurboExtendVideoConfig",
    INSERT_ID: "MinimaxH3MaxInsertVideoConfig",
    RECAST_ID: "MinimaxH3MaxRecastConfig",
    RELIGHT_ID: "MinimaxH3MaxRelightConfig",
    REFRAME_ID: "MinimaxH3MaxReframeVideoConfig",
    THREE_D_ID: "MinimaxH3Max3dToVideoConfig",
    LIP_SYNC_ID: "MinimaxH3MaxLipSyncImageToVideoConfig",
}

DEFAULT_PARAMETERS = {
    **{
        app_id: {
            "reference_audio_urls": [],
            "enable_prompt_expansion": True,
            "duration": 5,
            "resolution": "768P",
            "aspect_ratio": "auto",
            "seed": None,
            "output": "extended",
            "enable_safety_checker": True,
        }
        for app_id in EXTEND_IDS
    },
    INSERT_ID: {
        "prompt": None,
        "reference_image_urls": [],
        "reference_video_urls": [],
        "duration": 5,
        "resolution": "768p",
        "seed": None,
        "enable_prompt_expansion": True,
        "color_match": True,
    },
    RECAST_ID: {
        "prompt": None,
        "resolution": "1080P",
        "seed": None,
        "enhance_realism": False,
        "enable_safety_checker": True,
    },
    RELIGHT_ID: {
        "resolution": "768P",
        "aspect_ratio": "16:9",
        "seed": None,
        "enable_safety_checker": True,
        "sync_mode": False,
    },
    REFRAME_ID: {
        "prompt": "",
        "aspect_ratio": "16:9",
        "resolution": "768p",
        "seed": None,
        "enable_safety_checker": True,
    },
    THREE_D_ID: {
        "prompt": None,
        "reference_image_urls": [],
        "max_generated_reference_images": 2,
        "resolution": "768P",
        "enable_safety_checker": True,
    },
    LIP_SYNC_ID: {
        "resolution": "768P",
        "enable_transcription": True,
        "seed": None,
        "enable_safety_checker": True,
    },
}


@pytest.mark.parametrize("app_id", REQUIRED_PARAMETERS)
def test_video_editing_registers_and_routes_each_endpoint_with_its_defaults(app_id: str) -> None:
    parameters = REQUIRED_PARAMETERS[app_id]
    config = validate_parameters(app_id, parameters)
    parsed = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters})

    assert app_id in SUPPORTED_APP_IDS
    assert type(config).__name__ == EXPECTED_CLASSES[app_id]
    assert type(parsed) is type(config)
    assert config.model_dump() == {
        "app_id": app_id,
        **parameters,
        **DEFAULT_PARAMETERS[app_id],
    }
    assert config.random_seed_field == (None if app_id == THREE_D_ID else "seed")
    assert set(type(config).model_json_schema()["required"]) == {"app_id", *parameters}


@pytest.mark.parametrize(
    ("app_id", "missing"),
    [(app_id, key) for app_id, parameters in REQUIRED_PARAMETERS.items() for key in parameters],
)
def test_video_editing_requires_each_source_and_required_control(app_id: str, missing: str) -> None:
    parameters = {
        key: value for key, value in REQUIRED_PARAMETERS[app_id].items() if key != missing
    }
    assert config_class_for_app_id(app_id) is not None

    with pytest.raises(ValidationError) as exc:
        validate_parameters(app_id, parameters)

    assert any(
        error["loc"][-1:] == (missing,) and error["type"] == "missing"
        for error in exc.value.errors()
    )


ENUMS = {
    **{
        app_id: {
            "resolution": ["480P", "768P", "1080P", "2K"],
            "aspect_ratio": ["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"],
            "output": ["extended", "continuation"],
        }
        for app_id in EXTEND_IDS
    },
    INSERT_ID: {"resolution": ["480p", "768p"]},
    RECAST_ID: {"resolution": ["768P", "1080P"]},
    RELIGHT_ID: {
        "resolution": ["480P", "768P", "1080P", "2K"],
        "aspect_ratio": ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"],
    },
    REFRAME_ID: {
        "resolution": ["480p", "768p", "1080p"],
        "aspect_ratio": ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "9:21"],
    },
    THREE_D_ID: {"resolution": ["480P", "768P", "1080P"]},
    LIP_SYNC_ID: {"resolution": ["480P", "768P", "1080P", "2K"]},
}


@pytest.mark.parametrize(
    ("app_id", "field", "value"),
    [
        (app_id, field, value)
        for app_id, fields in ENUMS.items()
        for field, values in fields.items()
        for value in values
    ],
)
def test_video_editing_accepts_each_provider_enum_value(
    app_id: str, field: str, value: str
) -> None:
    config = validate_parameters(app_id, {**REQUIRED_PARAMETERS[app_id], field: value})

    assert config.model_dump()[field] == value


@pytest.mark.parametrize(
    ("app_id", "field"),
    [(app_id, field) for app_id, fields in ENUMS.items() for field in fields],
)
def test_video_editing_rejects_values_outside_each_enum(app_id: str, field: str) -> None:
    assert config_class_for_app_id(app_id) is not None

    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**REQUIRED_PARAMETERS[app_id], field: "unsupported"})


BOUNDARIES = [
    *[
        (app_id, field, value)
        for app_id in EXTEND_IDS
        for field, value in [
            ("duration", 0.71),
            ("duration", 15),
            ("prompt", "x" * 50_000),
            ("reference_audio_urls", [AUDIO] * 3),
            ("seed", -1),
        ]
    ],
    (INSERT_ID, "start_time", 1.625),
    (INSERT_ID, "start_time", 60),
    (INSERT_ID, "resume_time", 1.626),
    (INSERT_ID, "resume_time", 60),
    (INSERT_ID, "duration", 5),
    (INSERT_ID, "duration", 13),
    (INSERT_ID, "prompt", "x" * 50_000),
    (INSERT_ID, "prompt", None),
    (INSERT_ID, "reference_image_urls", [IMAGE] * 9),
    (INSERT_ID, "reference_video_urls", [VIDEO] * 3),
    (INSERT_ID, "seed", 0),
    (INSERT_ID, "seed", 2_147_483_647),
    (RECAST_ID, "reference_image_urls", [IMAGE]),
    (RECAST_ID, "reference_image_urls", [IMAGE] * 4),
    (RECAST_ID, "prompt", "x" * 2000),
    (RECAST_ID, "prompt", ""),
    (RECAST_ID, "seed", 0),
    (RECAST_ID, "seed", 2**40),
    (RELIGHT_ID, "seed", -1),
    (REFRAME_ID, "prompt", "x" * 50_000),
    (REFRAME_ID, "prompt", ""),
    (REFRAME_ID, "seed", 0),
    (REFRAME_ID, "seed", 4_294_967_295),
    (THREE_D_ID, "prompt", "x" * 2000),
    (THREE_D_ID, "prompt", ""),
    (THREE_D_ID, "reference_image_urls", [IMAGE] * 8),
    (THREE_D_ID, "max_generated_reference_images", 1),
    (THREE_D_ID, "max_generated_reference_images", 8),
    (LIP_SYNC_ID, "seed", 0),
    (LIP_SYNC_ID, "seed", 2_147_483_647),
]


@pytest.mark.parametrize(("app_id", "field", "value"), BOUNDARIES)
def test_video_editing_accepts_schema_boundaries(app_id: str, field: str, value: object) -> None:
    config = validate_parameters(app_id, {**REQUIRED_PARAMETERS[app_id], field: value})

    assert config.model_dump()[field] == value


INVALID_PARAMETERS = [
    *[
        (app_id, field, value)
        for app_id in EXTEND_IDS
        for field, value in [
            ("duration", 0.7),
            ("duration", 15.01),
            ("prompt", ""),
            ("prompt", "x" * 50_001),
            ("video_url", ""),
            ("reference_audio_urls", [AUDIO] * 4),
            ("reference_audio_urls", None),
        ]
    ],
    (INSERT_ID, "start_time", 1.624),
    (INSERT_ID, "start_time", 60.1),
    (INSERT_ID, "resume_time", 1.625),
    (INSERT_ID, "resume_time", 60.1),
    (INSERT_ID, "duration", 4.99),
    (INSERT_ID, "duration", 13.01),
    (INSERT_ID, "prompt", ""),
    (INSERT_ID, "prompt", "x" * 50_001),
    (INSERT_ID, "video_url", ""),
    (INSERT_ID, "reference_image_urls", [IMAGE] * 10),
    (INSERT_ID, "reference_video_urls", [VIDEO] * 4),
    (INSERT_ID, "reference_image_urls", None),
    (INSERT_ID, "reference_video_urls", None),
    (INSERT_ID, "seed", -1),
    (INSERT_ID, "seed", 2_147_483_648),
    (RECAST_ID, "reference_image_urls", []),
    (RECAST_ID, "reference_image_urls", [IMAGE] * 5),
    (RECAST_ID, "prompt", "x" * 2001),
    (RECAST_ID, "seed", -1),
    (RELIGHT_ID, "video_url", ""),
    (RELIGHT_ID, "reference_image_url", ""),
    (REFRAME_ID, "prompt", "x" * 50_001),
    (REFRAME_ID, "prompt", None),
    (REFRAME_ID, "seed", -1),
    (REFRAME_ID, "seed", 4_294_967_296),
    (THREE_D_ID, "prompt", "x" * 2001),
    (THREE_D_ID, "reference_image_urls", [IMAGE] * 9),
    (THREE_D_ID, "reference_image_urls", None),
    (THREE_D_ID, "max_generated_reference_images", 0),
    (THREE_D_ID, "max_generated_reference_images", 9),
    (LIP_SYNC_ID, "seed", -1),
    (LIP_SYNC_ID, "seed", 2_147_483_648),
    *[(app_id, "unexpected", True) for app_id in REQUIRED_PARAMETERS],
    (THREE_D_ID, "seed", 1),
]


@pytest.mark.parametrize(("app_id", "field", "value"), INVALID_PARAMETERS)
def test_video_editing_rejects_out_of_range_or_unsupported_parameters(
    app_id: str,
    field: str,
    value: object,
) -> None:
    assert config_class_for_app_id(app_id) is not None

    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**REQUIRED_PARAMETERS[app_id], field: value})


ALL_OPTIONS = {
    **{
        app_id: {
            "reference_audio_urls": [AUDIO],
            "enable_prompt_expansion": False,
            "duration": 6.25,
            "resolution": "2K",
            "aspect_ratio": "9:16",
            "seed": 42,
            "output": "continuation",
            "enable_safety_checker": False,
        }
        for app_id in EXTEND_IDS
    },
    INSERT_ID: {
        "prompt": "Add a scene in the forest.",
        "reference_image_urls": [IMAGE],
        "reference_video_urls": [VIDEO],
        "duration": 7.5,
        "resolution": "480p",
        "seed": 42,
        "enable_prompt_expansion": False,
        "color_match": False,
    },
    RECAST_ID: {
        "prompt": "Replace the person in the foreground.",
        "resolution": "768P",
        "seed": 42,
        "enhance_realism": True,
        "enable_safety_checker": False,
    },
    RELIGHT_ID: {
        "resolution": "2K",
        "aspect_ratio": "adaptive",
        "seed": 42,
        "enable_safety_checker": False,
        "sync_mode": True,
    },
    REFRAME_ID: {
        "prompt": "Extend the room into the new surroundings.",
        "aspect_ratio": "9:21",
        "resolution": "1080p",
        "seed": 42,
        "enable_safety_checker": False,
    },
    THREE_D_ID: {
        "prompt": "The moving block represents a walking person.",
        "reference_image_urls": [IMAGE],
        "max_generated_reference_images": 8,
        "resolution": "1080P",
        "enable_safety_checker": False,
    },
    LIP_SYNC_ID: {
        "resolution": "2K",
        "enable_transcription": False,
        "seed": 42,
        "enable_safety_checker": False,
    },
}


@pytest.mark.parametrize("app_id", REQUIRED_PARAMETERS)
def test_video_editing_preserves_all_explicit_options(app_id: str) -> None:
    parameters = {**REQUIRED_PARAMETERS[app_id], **ALL_OPTIONS[app_id]}
    config = validate_parameters(app_id, parameters)

    assert config.model_dump() == {"app_id": app_id, **parameters}


@pytest.mark.parametrize("app_id", REQUIRED_PARAMETERS)
def test_video_editing_is_listed_and_prints_a_job_yaml_example(app_id: str) -> None:
    runner = CliRunner()
    listed = runner.invoke(app, ["models"])
    example = runner.invoke(app, ["schema", app_id])

    assert listed.exit_code == 0
    assert app_id in listed.stdout.splitlines()
    assert example.exit_code == 0
    job = YAML(typ="safe").load(example.stdout)
    assert job["app_id"] == app_id
    assert set(job["parameters"]) == {
        *REQUIRED_PARAMETERS[app_id],
        *DEFAULT_PARAMETERS[app_id],
    }
    assert {"output_dir", "slug", "version"} <= job.keys()
