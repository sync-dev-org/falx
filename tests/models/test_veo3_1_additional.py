from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    FalConfig,
    config_class_for_app_id,
    validate_parameters,
)

TEXT_APP_IDS = (
    "fal-ai/veo3.1",
    "fal-ai/veo3.1/fast",
    "fal-ai/veo3.1/lite",
)
IMAGE_APP_IDS = (
    "fal-ai/veo3.1/image-to-video",
    "fal-ai/veo3.1/fast/image-to-video",
    "fal-ai/veo3.1/lite/image-to-video",
)
FRAME_APP_IDS = (
    "fal-ai/veo3.1/first-last-frame-to-video",
    "fal-ai/veo3.1/fast/first-last-frame-to-video",
    "fal-ai/veo3.1/lite/first-last-frame-to-video",
)
REFERENCE_APP_IDS = (
    "fal-ai/veo3.1/reference-to-video",
    "fal-ai/veo3.1/fast/reference-to-video",
)
EXTEND_APP_IDS = (
    "fal-ai/veo3.1/extend-video",
    "fal-ai/veo3.1/fast/extend-video",
)
APP_IDS = TEXT_APP_IDS + IMAGE_APP_IDS + FRAME_APP_IDS + REFERENCE_APP_IDS + EXTEND_APP_IDS

REQUIRED_MEDIA = {
    **dict.fromkeys(TEXT_APP_IDS, {}),
    **dict.fromkeys(IMAGE_APP_IDS, {"image_url": "https://example.com/start.png"}),
    **dict.fromkeys(
        FRAME_APP_IDS,
        {
            "first_frame_url": "https://example.com/first.png",
            "last_frame_url": "https://example.com/last.png",
        },
    ),
    **dict.fromkeys(REFERENCE_APP_IDS, {"image_urls": ["https://example.com/ref.png"]}),
    **dict.fromkeys(EXTEND_APP_IDS, {"video_url": "https://example.com/input.mp4"}),
}


def parameters_for(app_id: str) -> dict[str, object]:
    return {"prompt": "A quiet forest at dawn.", **REQUIRED_MEDIA[app_id]}


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veo3_1_endpoints_register_and_validate_defaults(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    parameters = parameters_for(app_id)
    parsed = TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters})
    assert type(parsed) is config_class
    expected = {
        "app_id": app_id,
        **parameters,
        "aspect_ratio": "auto"
        if app_id in IMAGE_APP_IDS + FRAME_APP_IDS + EXTEND_APP_IDS
        else "16:9",
        "duration": "7s" if app_id in EXTEND_APP_IDS else "8s",
        "resolution": "720p",
        "generate_audio": True,
        "auto_fix": app_id in TEXT_APP_IDS,
        "safety_tolerance": "4",
    }
    if app_id not in REFERENCE_APP_IDS:
        expected.update(seed=None, negative_prompt=None)
    assert parsed.model_dump() == expected
    assert validate_parameters(app_id, parameters) == parsed
    assert config_class.random_seed_field == (None if app_id in REFERENCE_APP_IDS else "seed")


@pytest.mark.parametrize(
    ("app_id", "missing"),
    [(app_id, field) for app_id in APP_IDS for field in ("prompt", *REQUIRED_MEDIA[app_id])],
)
def test_veo3_1_endpoints_reject_missing_required_inputs(app_id: str, missing: str) -> None:
    parameters = parameters_for(app_id)
    del parameters[missing]
    with pytest.raises(ValidationError) as error:
        validate_parameters(app_id, parameters)
    assert any(
        item["loc"][-1] == missing and item["type"] == "missing" for item in error.value.errors()
    )


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veo3_1_prompt_accepts_20000_characters_and_rejects_20001(app_id: str) -> None:
    parameters = parameters_for(app_id)
    parameters["prompt"] = "x" * 20_000
    parsed = validate_parameters(app_id, parameters)
    assert parsed is not None
    assert parsed.prompt == parameters["prompt"]
    parameters["prompt"] += "x"
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(app_id, parameters)


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aspect_ratio", "1:1"),
        ("duration", "12s"),
        ("resolution", "480p"),
        ("safety_tolerance", "7"),
        ("unknown_parameter", True),
    ],
)
def test_veo3_1_endpoints_reject_invalid_parameters(
    app_id: str,
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(app_id, {**parameters_for(app_id), field: value})


@pytest.mark.parametrize("app_id", TEXT_APP_IDS + IMAGE_APP_IDS + FRAME_APP_IDS)
@pytest.mark.parametrize("duration", ["4s", "6s", "8s"])
def test_veo3_1_generation_accepts_all_durations(app_id: str, duration: str) -> None:
    config = validate_parameters(app_id, {**parameters_for(app_id), "duration": duration})
    assert config is not None
    assert config.duration == duration


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("resolution", ["720p", "1080p", "4k"])
def test_veo3_1_resolution_support_depends_on_endpoint(app_id: str, resolution: str) -> None:
    parameters = {**parameters_for(app_id), "resolution": resolution}
    rejected = (
        app_id in EXTEND_APP_IDS
        and resolution != "720p"
        or app_id.startswith("fal-ai/veo3.1/lite")
        and resolution == "4k"
    )
    if rejected:
        with pytest.raises(ValidationError, match="resolution"):
            validate_parameters(app_id, parameters)
    else:
        config = validate_parameters(app_id, parameters)
        assert config is not None
        assert config.resolution == resolution


@pytest.mark.parametrize("app_id", REFERENCE_APP_IDS + EXTEND_APP_IDS)
@pytest.mark.parametrize("duration", ["4s", "6s", "7s", "8s"])
def test_veo3_1_reference_and_extension_require_fixed_duration(app_id: str, duration: str) -> None:
    parameters = {**parameters_for(app_id), "duration": duration}
    expected = "7s" if app_id in EXTEND_APP_IDS else "8s"
    if duration != expected:
        with pytest.raises(ValidationError, match="duration"):
            validate_parameters(app_id, parameters)
    else:
        config = validate_parameters(app_id, parameters)
        assert config is not None
        assert config.duration == expected


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("aspect_ratio", ["auto", "16:9", "9:16"])
def test_veo3_1_aspect_ratio_support_depends_on_endpoint(app_id: str, aspect_ratio: str) -> None:
    parameters = {**parameters_for(app_id), "aspect_ratio": aspect_ratio}
    if aspect_ratio == "auto" and app_id in TEXT_APP_IDS + REFERENCE_APP_IDS:
        with pytest.raises(ValidationError, match="aspect_ratio"):
            validate_parameters(app_id, parameters)
    else:
        config = validate_parameters(app_id, parameters)
        assert config is not None
        assert config.aspect_ratio == aspect_ratio


@pytest.mark.parametrize("app_id", APP_IDS)
@pytest.mark.parametrize("safety_tolerance", ["1", "2", "3", "4", "5", "6"])
def test_veo3_1_accepts_all_safety_tolerance_values(app_id: str, safety_tolerance: str) -> None:
    config = validate_parameters(
        app_id,
        {**parameters_for(app_id), "safety_tolerance": safety_tolerance},
    )
    assert config is not None
    assert config.safety_tolerance == safety_tolerance


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veo3_1_optional_parameters_follow_endpoint_contract(app_id: str) -> None:
    parameters = {**parameters_for(app_id), "generate_audio": False, "auto_fix": True}
    if app_id in REFERENCE_APP_IDS:
        for field, value in (("seed", 42), ("negative_prompt", "blur")):
            with pytest.raises(ValidationError, match=field):
                validate_parameters(app_id, {**parameters, field: value})
    else:
        parameters.update(seed=-1, negative_prompt="blur")
    config = validate_parameters(app_id, parameters)
    assert config is not None
    assert config.generate_audio is False
    assert config.auto_fix is True
    if app_id not in REFERENCE_APP_IDS:
        assert config.seed == -1
        assert config.negative_prompt == "blur"


@pytest.mark.parametrize("app_id", APP_IDS)
def test_veo3_1_schema_describes_current_upstream_fields(app_id: str) -> None:
    config_class = config_class_for_app_id(app_id)
    assert config_class is not None
    fields = config_class.model_fields
    assert fields["safety_tolerance"].description == (
        "The safety tolerance level for content moderation. "
        "1 is the most strict (blocks most content), 6 is the least strict."
    )
    assert fields["duration"].description == "The duration of the generated video."
    assert fields["resolution"].description == "The resolution of the generated video."
    if app_id in EXTEND_APP_IDS:
        prompt_description = "The text prompt describing how the video should be extended"
    elif app_id == "fal-ai/veo3.1/lite/image-to-video":
        prompt_description = "The text prompt describing how the image should be animated"
    else:
        prompt_description = "The text prompt describing the video you want to generate"
    assert fields["prompt"].description == prompt_description
    if app_id in TEXT_APP_IDS:
        aspect_description = "Aspect ratio of the generated video"
    elif app_id in IMAGE_APP_IDS[:2]:
        aspect_description = (
            "The aspect ratio of the generated video. Only 16:9 and 9:16 are supported."
        )
    else:
        aspect_description = "The aspect ratio of the generated video."
    assert fields["aspect_ratio"].description == aspect_description
    if app_id in IMAGE_APP_IDS:
        image_description = (
            "URL of the input image to animate. Should be 720p or higher resolution "
            "in 16:9 or 9:16 aspect ratio."
        )
        if app_id in IMAGE_APP_IDS[:2]:
            image_description += (
                " If the image is not in 16:9 or 9:16 aspect ratio, it will be cropped to fit."
            )
        assert fields["image_url"].description == image_description
    if app_id in FRAME_APP_IDS:
        assert fields["first_frame_url"].description == "URL of the first frame of the video"
        assert fields["last_frame_url"].description == "URL of the last frame of the video"
    if app_id in REFERENCE_APP_IDS:
        assert fields["image_urls"].description == (
            "URLs of the reference images to use for consistent subject appearance"
        )
    if app_id in EXTEND_APP_IDS:
        assert fields["video_url"].description == (
            "URL of the video to extend. The video should be 720p or 1080p resolution "
            "in 16:9 or 9:16 aspect ratio."
        )
