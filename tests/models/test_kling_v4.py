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

# Contract: Kling 4.0 and Flash input schemas and endpoint registration.
STANDARD = "kling/v4/"
FLASH = "kling/v4/flash/"
APP_IDS = (
    STANDARD + "text-to-video",
    STANDARD + "image-to-video",
    STANDARD + "reference-to-video",
    STANDARD + "video-to-video/edit",
    FLASH + "text-to-video",
    FLASH + "image-to-video",
    FLASH + "reference-to-video",
    FLASH + "video-to-video",
)
GENERATION_IDS = tuple(app_id for app_id in APP_IDS if "video-to-video" not in app_id)
REFERENCE_IDS = tuple(app_id for app_id in APP_IDS if "reference-to-video" in app_id)
EDIT_IDS = tuple(app_id for app_id in APP_IDS if "video-to-video" in app_id)
REFERENCED_IDS = REFERENCE_IDS + EDIT_IDS
MULTI_SHOT_IDS = tuple(app_id for app_id in GENERATION_IDS if "/flash/" not in app_id)


def minimal_parameters(app_id: str) -> dict[str, object]:
    if app_id.endswith("image-to-video"):
        return {"start_image_url": "https://example.com/start.png"}
    if app_id in EDIT_IDS:
        return {"prompt": "Edit @Video1.", "video_url": "https://example.com/source.mp4"}
    return {"prompt": "A continuous tracking shot."}


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_registers_and_routes_each_endpoint(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class.random_seed_field is None
    config = TypeAdapter(FalConfig).validate_python(
        {"app_id": app_id, **minimal_parameters(app_id)}
    )
    assert type(config) is config_class
    assert config.app_id == app_id


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_defaults_match_each_generation_mode(app_id: str) -> None:
    config = validate_parameters(app_id, minimal_parameters(app_id))
    assert config is not None
    expected: dict[str, object] = {
        "app_id": app_id,
        **minimal_parameters(app_id),
        "duration": None if app_id in EDIT_IDS else 5,
        "resolution": "720p" if "/flash/" in app_id else "1080p",
    }
    if "/flash/" not in app_id:
        expected["hdr"] = False
    if app_id in MULTI_SHOT_IDS:
        expected["multi_prompt"] = None
    if app_id.endswith("image-to-video"):
        expected["prompt"] = None
        if "/flash/" not in app_id:
            expected.update(end_image_url=None, middle_image_urls=None)
    elif app_id not in EDIT_IDS:
        expected["aspect_ratio"] = "16:9"
    if app_id in REFERENCED_IDS:
        expected.update(elements=None, image_urls=None, video_urls=None, keep_audio=False)
        if app_id in REFERENCE_IDS:
            expected["start_image_url"] = None
        if "/flash/" not in app_id:
            expected.update(
                start_image_url=None, end_image_url=None, middle_image_urls=None, voice_ids=None
            )
            if app_id in EDIT_IDS:
                expected["aspect_ratio"] = None
    assert config.model_dump() == expected


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_rejects_missing_inputs(app_id: str) -> None:
    parameters = minimal_parameters(app_id)
    for field in parameters:
        with pytest.raises(ValidationError, match=field):
            validate_parameters(app_id, {k: v for k, v in parameters.items() if k != field})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("duration", [2, 31, 3.5])
def test_kling_v4_rejects_invalid_durations(app_id: str, duration: float) -> None:
    with pytest.raises(ValidationError, match="duration"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "duration": duration})


@pytest.mark.parametrize("app_id", tuple(app_id for app_id in APP_IDS if "/flash/" in app_id))
def test_kling_v4_flash_rejects_duration_above_twenty_seconds(app_id: str) -> None:
    with pytest.raises(ValidationError, match="duration"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "duration": 21})


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("at_maximum", [False, True])
def test_kling_v4_accepts_duration_boundaries(app_id: str, at_maximum: bool) -> None:
    duration = (20 if "/flash/" in app_id else 30) if at_maximum else 3
    config = validate_parameters(app_id, {**minimal_parameters(app_id), "duration": duration})
    assert config is not None
    assert config.duration == duration


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_rejects_overlong_prompts(app_id: str) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "prompt": "x" * 26001})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_rejects_unsupported_resolutions(app_id: str) -> None:
    resolution = "1080p" if "/flash/" in app_id else "2160p"
    with pytest.raises(ValidationError, match="resolution"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "resolution": resolution})


@pytest.mark.parametrize("app_id", tuple(app_id for app_id in APP_IDS if "/flash/" not in app_id))
def test_kling_v4_hdr_requires_1080p_or_4k(app_id: str) -> None:
    with pytest.raises(ValidationError, match="hdr"):
        validate_parameters(
            app_id, {**minimal_parameters(app_id), "resolution": "720p", "hdr": True}
        )
    config = validate_parameters(
        app_id, {**minimal_parameters(app_id), "resolution": "4k", "hdr": True}
    )
    assert config is not None
    assert config.hdr is True


@pytest.mark.parametrize("app_id", MULTI_SHOT_IDS)
def test_kling_v4_accepts_multi_shot_input_without_top_level_prompt(app_id: str) -> None:
    parameters = minimal_parameters(app_id)
    parameters.pop("prompt", None)
    parameters["multi_prompt"] = [{"prompt": "Opening shot."}, {"prompt": "Closing shot."}]
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.prompt is None
    assert config.model_dump()["multi_prompt"] == [
        {"prompt": "Opening shot.", "duration": 5},
        {"prompt": "Closing shot.", "duration": 5},
    ]


@pytest.mark.parametrize("app_id", MULTI_SHOT_IDS)
@pytest.mark.parametrize(
    "multi_prompt",
    [
        [],
        [{}],
        [{"prompt": ""}],
        [{"prompt": "x" * 513}],
        [{"prompt": "Shot", "duration": 0}],
        [{"prompt": "Shot", "duration": 31}],
    ],
)
def test_kling_v4_rejects_invalid_shots(app_id: str, multi_prompt: list[object]) -> None:
    with pytest.raises(ValidationError, match="multi_prompt"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "multi_prompt": multi_prompt})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_rejects_unsupported_aspect_ratios(app_id: str) -> None:
    with pytest.raises(ValidationError, match="aspect_ratio"):
        validate_parameters(app_id, {**minimal_parameters(app_id), "aspect_ratio": "2:1"})


@pytest.mark.parametrize("app_id", REFERENCE_IDS)
def test_kling_v4_accepts_auto_aspect_ratio_for_references(app_id: str) -> None:
    config = validate_parameters(app_id, {**minimal_parameters(app_id), "aspect_ratio": "auto"})
    assert config is not None
    assert config.aspect_ratio == "auto"


@pytest.mark.parametrize("app_id", REFERENCED_IDS)
@pytest.mark.parametrize("field", ["elements", "image_urls", "video_urls"])
def test_kling_v4_rejects_too_many_references(app_id: str, field: str) -> None:
    limit = {"elements": 7, "image_urls": 10, "video_urls": 4 if app_id in EDIT_IDS else 5}[field]
    item = {"frontal_image_url": "https://example.com/actor.png"} if field == "elements" else "url"
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**minimal_parameters(app_id), field: [item] * (limit + 1)})


@pytest.mark.parametrize("app_id", REFERENCED_IDS)
def test_kling_v4_accepts_elements_and_all_reference_types(app_id: str) -> None:
    config = validate_parameters(
        app_id,
        {
            **minimal_parameters(app_id),
            "elements": [
                {
                    "frontal_image_url": "https://example.com/actor.png",
                    "reference_image_urls": ["https://example.com/side.png"],
                },
                {"video_url": "https://example.com/actor.mp4"},
            ],
            "image_urls": ["https://example.com/style.png"],
            "video_urls": ["https://example.com/reference.mp4"],
            "keep_audio": True,
        },
    )
    assert config is not None
    assert config.model_dump()["elements"][1]["video_url"] == "https://example.com/actor.mp4"
    assert config.keep_audio is True


@pytest.mark.parametrize("app_id", REFERENCED_IDS)
def test_kling_v4_rejects_too_many_element_images(app_id: str) -> None:
    with pytest.raises(ValidationError, match="reference_image_urls"):
        validate_parameters(
            app_id,
            {
                **minimal_parameters(app_id),
                "elements": [{"reference_image_urls": ["image"] * 4}],
            },
        )


@pytest.mark.parametrize(
    "app_id", tuple(app_id for app_id in REFERENCED_IDS if "/flash/" in app_id)
)
def test_kling_v4_flash_rejects_bound_voices(app_id: str) -> None:
    with pytest.raises(ValidationError, match="voice_id"):
        validate_parameters(
            app_id,
            {
                **minimal_parameters(app_id),
                "elements": [{"frontal_image_url": "image", "voice_id": "speaker"}],
            },
        )


@pytest.mark.parametrize(
    "app_id", tuple(app_id for app_id in REFERENCED_IDS if "/flash/" not in app_id)
)
def test_kling_v4_accepts_bound_voices_and_rejects_too_many_voices(app_id: str) -> None:
    parameters = {
        **minimal_parameters(app_id),
        "elements": [{"frontal_image_url": "image", "voice_id": "actor"}],
        "voice_ids": ["narrator"],
    }
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.model_dump()["elements"][0]["voice_id"] == "actor"
    with pytest.raises(ValidationError, match="voice"):
        validate_parameters(app_id, {**parameters, "voice_ids": ["v"] * 4})


@pytest.mark.parametrize("app_id", MULTI_SHOT_IDS[1:] + (STANDARD + "video-to-video/edit",))
def test_kling_v4_rejects_more_than_eight_middle_frames(app_id: str) -> None:
    with pytest.raises(ValidationError, match="middle_image_urls"):
        validate_parameters(
            app_id,
            {
                **minimal_parameters(app_id),
                "middle_image_urls": ["frame"] * 9,
            },
        )


@pytest.mark.parametrize("app_id", REFERENCED_IDS)
def test_kling_v4_rejects_more_than_three_video_elements(app_id: str) -> None:
    with pytest.raises(ValidationError, match="video elements"):
        validate_parameters(
            app_id,
            {
                **minimal_parameters(app_id),
                "elements": [{"video_url": "video"}] * 4,
            },
        )


@pytest.mark.parametrize("app_id", REFERENCED_IDS)
def test_kling_v4_element_views_require_one_to_three_images(app_id: str) -> None:
    with pytest.raises(ValidationError, match="reference_image_urls"):
        validate_parameters(
            app_id,
            {
                **minimal_parameters(app_id),
                "elements": [{"reference_image_urls": []}],
            },
        )


@pytest.mark.parametrize("app_id", REFERENCE_IDS + (STANDARD + "video-to-video/edit",))
def test_kling_v4_counts_keyframes_toward_ten_reference_images(app_id: str) -> None:
    parameters = {
        **minimal_parameters(app_id),
        "start_image_url": "frame",
        "image_urls": ["image"] * 9,
    }
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert len(config.image_urls) == 9
    with pytest.raises(ValidationError, match="image reference"):
        validate_parameters(app_id, {**parameters, "image_urls": ["image"] * 10})


@pytest.mark.parametrize(
    "app_id", (STANDARD + "reference-to-video", STANDARD + "video-to-video/edit")
)
def test_kling_v4_counts_middle_and_end_frames_toward_reference_images(app_id: str) -> None:
    with pytest.raises(ValidationError, match="image reference"):
        validate_parameters(
            app_id,
            {
                **minimal_parameters(app_id),
                "start_image_url": "first",
                "middle_image_urls": ["middle"] * 8,
                "end_image_url": "last",
                "image_urls": ["extra"],
            },
        )


@pytest.mark.parametrize(
    "app_id", (STANDARD + "reference-to-video", STANDARD + "video-to-video/edit")
)
@pytest.mark.parametrize(
    "voices",
    [
        {"elements": [{"voice_id": "actor"}] * 4},
        {"elements": [{"voice_id": "actor"}] * 2, "voice_ids": ["one", "two"]},
        {"elements": [{"voice_id": "actor"}], "keep_audio": True},
        {"voice_ids": ["speaker"], "keep_audio": True},
    ],
)
def test_kling_v4_rejects_combined_voice_limits_and_retained_audio(
    app_id: str,
    voices: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="voice"):
        validate_parameters(app_id, {**minimal_parameters(app_id), **voices})


@pytest.mark.parametrize("app_id", MULTI_SHOT_IDS)
@pytest.mark.parametrize("durations", [(1,), (15, 16)])
def test_kling_v4_limits_total_multi_shot_duration(app_id: str, durations: tuple[int, ...]) -> None:
    parameters = minimal_parameters(app_id)
    parameters.pop("prompt", None)
    parameters["multi_prompt"] = [{"prompt": "Shot", "duration": value} for value in durations]
    with pytest.raises(ValidationError, match="multi_prompt.*duration"):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_v4_schema_command_emits_job_yaml_with_parameters(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"]["resolution"] == ("720p" if "/flash/" in app_id else "1080p")
    assert payload["parameters"]["duration"] == (None if app_id in EDIT_IDS else 5)
    assert "app_id" not in payload["parameters"]


def test_kling_v4_models_command_lists_all_eight_endpoints() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())
