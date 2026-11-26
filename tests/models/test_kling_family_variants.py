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
)

O3_STANDARD_GENERATORS = [
    f"fal-ai/kling-video/o3/standard/{mode}-to-video" for mode in ("text", "image", "reference")
]
O3_VIDEO_EDIT = "fal-ai/kling-video/o3/standard/video-to-video/edit"
O3_VIDEO_REFERENCES = [
    f"fal-ai/kling-video/o3/{tier}/video-to-video/reference" for tier in ("standard", "pro")
]
V3_STANDARD_GENERATORS = [
    f"fal-ai/kling-video/v3/standard/{mode}-to-video" for mode in ("text", "image")
]
V3_MOTION = "fal-ai/kling-video/v3/standard/motion-control"
V3_TURBO_GENERATORS = [
    f"fal-ai/kling-video/v3/turbo/{tier}/{mode}-to-video"
    for tier in ("standard", "pro")
    for mode in ("text", "image")
]
APP_IDS = [
    *O3_STANDARD_GENERATORS,
    O3_VIDEO_EDIT,
    *O3_VIDEO_REFERENCES,
    *V3_STANDARD_GENERATORS,
    V3_MOTION,
    *V3_TURBO_GENERATORS,
]
GENERATORS = [*O3_STANDARD_GENERATORS, *V3_STANDARD_GENERATORS, *V3_TURBO_GENERATORS]
VIDEO_INPUTS = [O3_VIDEO_EDIT, *O3_VIDEO_REFERENCES]
PROMPT = "A heron takes flight."
IMAGE_URL = "https://example.com/first.png"
VIDEO_URL = "https://example.com/reference.mp4"


def minimal_parameters(app_id: str) -> dict[str, object]:
    if app_id == V3_MOTION:
        return {
            "image_url": IMAGE_URL,
            "video_url": VIDEO_URL,
            "character_orientation": "image",
        }
    parameters: dict[str, object] = {"prompt": PROMPT}
    if app_id in VIDEO_INPUTS:
        parameters["video_url"] = VIDEO_URL
    elif app_id.endswith("/image-to-video"):
        key = "start_image_url" if app_id in V3_STANDARD_GENERATORS else "image_url"
        parameters[key] = IMAGE_URL
    return parameters


def parse(app_id: str, **overrides: object):
    return TypeAdapter(FalConfig).validate_python(
        {"app_id": app_id, **minimal_parameters(app_id), **overrides}
    )


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_variants_route_to_registered_configs_with_schema_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    assert config_class.random_seed_field is None
    config = parse(app_id)
    assert type(config) is config_class
    expected = {"app_id": app_id, **minimal_parameters(app_id), "enable_safety_checker": True}
    if app_id == V3_MOTION:
        expected.update(prompt=None, elements=None, keep_original_sound=True)
    elif app_id in VIDEO_INPUTS:
        expected.update(shot_type="customize", keep_audio=True, elements=None, image_urls=None)
        if app_id in O3_VIDEO_REFERENCES:
            expected.update(aspect_ratio="auto", duration=None)
    else:
        expected.update(duration="5", multi_prompt=None)
        if app_id not in V3_TURBO_GENERATORS:
            expected.update(shot_type="customize", generate_audio=app_id in V3_STANDARD_GENERATORS)
        if app_id in V3_STANDARD_GENERATORS:
            expected.update(negative_prompt="blur, distort, and low quality", cfg_scale=0.5)
        if app_id.endswith("/text-to-video") or app_id.endswith("/reference-to-video"):
            expected["aspect_ratio"] = "16:9"
        if app_id.endswith("/image-to-video") and app_id not in V3_TURBO_GENERATORS:
            expected["end_image_url"] = None
        if app_id.endswith("/reference-to-video"):
            expected.update(
                start_image_url=None, end_image_url=None, elements=None, image_urls=None
            )
        if app_id == "fal-ai/kling-video/v3/standard/image-to-video":
            expected["elements"] = None
    assert config.model_dump() == expected
    assert parse(app_id, enable_safety_checker=False).enable_safety_checker is False


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_variants_limit_prompt_length_and_reject_unknown_parameters(app_id: str) -> None:
    limit = 3072 if app_id in V3_TURBO_GENERATORS else 2500
    assert parse(app_id, prompt="x" * limit).prompt == "x" * limit
    with pytest.raises(ValidationError, match="prompt"):
        parse(app_id, prompt="x" * (limit + 1))
    with pytest.raises(ValidationError, match="unexpected"):
        parse(app_id, unexpected=True)


REQUIRED_FIELDS = [
    ("fal-ai/kling-video/o3/standard/image-to-video", "image_url"),
    ("fal-ai/kling-video/v3/standard/image-to-video", "start_image_url"),
    *[(app_id, field) for app_id in VIDEO_INPUTS for field in ("prompt", "video_url")],
    *[(V3_MOTION, field) for field in ("image_url", "video_url", "character_orientation")],
    *[(app_id, "image_url") for app_id in V3_TURBO_GENERATORS if "/image-to-video" in app_id],
]


@pytest.mark.parametrize(("app_id", "field"), REQUIRED_FIELDS)
def test_kling_variants_reject_missing_required_inputs(app_id: str, field: str) -> None:
    payload = {"app_id": app_id, **minimal_parameters(app_id)}
    del payload[field]
    with pytest.raises(ValidationError, match=field):
        TypeAdapter(FalConfig).validate_python(payload)


@pytest.mark.parametrize("app_id", [*GENERATORS, *O3_VIDEO_REFERENCES])
def test_kling_variants_accept_duration_enum_and_reject_outside_values(app_id: str) -> None:
    for duration in map(str, range(3, 16)):
        assert parse(app_id, duration=duration).duration == duration
    for duration in ("2", "16", 5):
        with pytest.raises(ValidationError, match="duration"):
            parse(app_id, duration=duration)
    if app_id in O3_VIDEO_REFERENCES:
        assert parse(app_id, duration=None).duration is None


@pytest.mark.parametrize("app_id", GENERATORS)
def test_kling_variants_accept_storyboards_and_reject_conflicting_prompts(app_id: str) -> None:
    config = parse(app_id, prompt=None, multi_prompt=[{"prompt": "A close-up.", "duration": "1"}])
    assert config.multi_prompt[0].duration == "1"
    with pytest.raises(ValidationError, match="not both|mutually exclusive"):
        parse(app_id, multi_prompt=[{"prompt": "A close-up."}])
    with pytest.raises(ValidationError, match="prompt"):
        parse(app_id, prompt=None, multi_prompt=[{"duration": "3"}])
    with pytest.raises(ValidationError, match="duration"):
        parse(app_id, prompt=None, multi_prompt=[{"prompt": PROMPT, "duration": "16"}])
    if app_id not in V3_TURBO_GENERATORS:
        with pytest.raises(ValidationError, match="prompt or multi_prompt"):
            parse(app_id, prompt=None)


@pytest.mark.parametrize("app_id", V3_TURBO_GENERATORS)
def test_kling_turbo_bounds_storyboard_shots_and_total_duration(app_id: str) -> None:
    assert parse(app_id, prompt=None).prompt is None
    shots = [{"prompt": PROMPT, "duration": "2"}] * 6
    assert len(parse(app_id, prompt=None, multi_prompt=shots).multi_prompt) == 6
    assert parse(app_id, prompt=None, multi_prompt=[{"prompt": PROMPT, "duration": "15"}])
    for invalid in ([], shots + shots[:1], [{"prompt": PROMPT, "duration": "8"}] * 2):
        with pytest.raises(ValidationError, match="multi_prompt|15"):
            parse(app_id, prompt=None, multi_prompt=invalid)
    for unsupported in ("generate_audio", "cfg_scale", "shot_type", "elements", "end_image_url"):
        with pytest.raises(ValidationError, match=unsupported):
            parse(app_id, **{unsupported: None})


@pytest.mark.parametrize("app_id", V3_STANDARD_GENERATORS)
def test_kling_v3_standard_bounds_cfg_scale_and_negative_prompt(app_id: str) -> None:
    for cfg_scale in (0, 1):
        assert parse(app_id, cfg_scale=cfg_scale).cfg_scale == cfg_scale
    for cfg_scale in (-0.1, 1.1):
        with pytest.raises(ValidationError, match="cfg_scale"):
            parse(app_id, cfg_scale=cfg_scale)
    assert parse(app_id, negative_prompt="x" * 2500).negative_prompt == "x" * 2500
    with pytest.raises(ValidationError, match="negative_prompt"):
        parse(app_id, negative_prompt="x" * 2501)


@pytest.mark.parametrize(
    "app_id",
    [app_id for app_id in GENERATORS if not app_id.endswith("/image-to-video")]
    + O3_VIDEO_REFERENCES,
)
def test_kling_variants_validate_aspect_ratio(app_id: str) -> None:
    ratios = ["16:9", "9:16", "1:1"]
    if app_id in O3_VIDEO_REFERENCES:
        ratios.append("auto")
    for aspect_ratio in ratios:
        assert parse(app_id, aspect_ratio=aspect_ratio).aspect_ratio == aspect_ratio
    with pytest.raises(ValidationError, match="aspect_ratio"):
        parse(app_id, aspect_ratio="4:3")


@pytest.mark.parametrize("app_id", VIDEO_INPUTS)
def test_kling_o3_video_inputs_validate_references_and_edit_shot_type(app_id: str) -> None:
    config = parse(
        app_id,
        prompt="Use @Element1 and @Image1.",
        elements=[{"reference_image_urls": [IMAGE_URL]}],
        image_urls=[IMAGE_URL],
    )
    assert config.elements[0].reference_image_urls == [IMAGE_URL]
    for fields in (
        {"shot_type": "intelligent"},
        {"prompt": "Use @Element1."},
        {"prompt": "Use @Image1."},
        {"elements": [{}]},
        {"elements": [{"reference_image_urls": []}]},
        {"elements": [{"reference_image_urls": [IMAGE_URL] * 4}]},
        {"elements": [{"video_url": VIDEO_URL}]},
        {"elements": [{"frontal_image_url": IMAGE_URL}], "image_urls": [IMAGE_URL] * 4},
    ):
        with pytest.raises(ValidationError):
            parse(app_id, **fields)


def test_kling_standard_reference_inputs_validate_combo_elements() -> None:
    for app_id in (
        "fal-ai/kling-video/o3/standard/reference-to-video",
        "fal-ai/kling-video/v3/standard/image-to-video",
    ):
        valid = [{"video_url": VIDEO_URL, "voice_id": "voice-1"}]
        assert (
            parse(app_id, prompt="Use @Element1.", elements=valid).elements[0].voice_id == "voice-1"
        )
        for elements in (
            valid * 2,
            [{}],
            [{"frontal_image_url": IMAGE_URL, "voice_id": "voice-1"}],
        ):
            with pytest.raises(ValidationError):
                parse(app_id, elements=elements)
    with pytest.raises(ValidationError, match="Maximum 4"):
        parse(
            "fal-ai/kling-video/o3/standard/reference-to-video",
            elements=[{"video_url": VIDEO_URL}],
            image_urls=[IMAGE_URL] * 4,
        )


def test_kling_standard_motion_requires_video_orientation_for_one_facial_element() -> None:
    elements = [{"frontal_image_url": IMAGE_URL}]
    assert parse(V3_MOTION, character_orientation="video", elements=elements).elements
    for fields in (
        {"elements": elements},
        {"character_orientation": "front"},
        {"character_orientation": "video", "elements": elements * 2},
        {"character_orientation": "video", "elements": [{}]},
    ):
        with pytest.raises(ValidationError):
            parse(V3_MOTION, **fields)


@pytest.mark.parametrize("app_id", APP_IDS)
def test_kling_variants_print_job_schema_examples(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0, result.output
    example = YAML(typ="safe").load(result.output)
    assert example["app_id"] == app_id
    assert example["parameters"]["enable_safety_checker"] is True
    assert example["version"] == 1
    assert "random_seed_field" not in example["parameters"]


def test_kling_variants_appear_in_models_command() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0, result.output
    assert set(APP_IDS) <= set(result.output.splitlines())
