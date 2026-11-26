from __future__ import annotations

from typing import Literal

import pytest
from pydantic import BaseModel, Field, create_model
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import _build_schema_example_yaml, app
from falx.models import SUPPORTED_APP_IDS, Flux3KeyframesToVideoConfig, validate_parameters
from falx.models.kling_o3_common import KlingO3MultiPromptElement
from falx.models.kling_v3_common import KlingV3MultiPromptElement

runner = CliRunner()
safe_yaml = YAML(typ="safe")


@pytest.mark.parametrize("app_id", sorted(SUPPORTED_APP_IDS))
def test_schema_prints_parameters_accepted_by_the_model(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    validate_parameters(app_id, payload["parameters"])


@pytest.mark.parametrize(
    ("annotation", "constraints"),
    [
        (int, {"ge": 2}),
        (int, {"gt": 2}),
        (int, {"le": -2}),
        (int, {"lt": -2}),
        (float, {"ge": 1.625}),
        (float, {"gt": 1.625}),
        (float, {"le": -1.625}),
        (float, {"lt": -1.625}),
        (float, {"gt": 1.625, "lt": 1.626}),
    ],
)
def test_schema_example_numbers_satisfy_their_bounds(
    annotation: type[int] | type[float], constraints: dict[str, float]
) -> None:
    config_class = create_model(
        "BoundedNumberConfig",
        app_id=(Literal["example/model"], ...),
        value=(annotation, Field(..., **constraints)),
    )

    payload = safe_yaml.load(_build_schema_example_yaml(config_class, "example/model"))

    assert type(payload["parameters"]["value"]) is annotation
    config_class.model_validate({"app_id": payload["app_id"], **payload["parameters"]})


def test_schema_example_uses_the_first_choice_for_required_enum_fields() -> None:
    class ChoicesConfig(BaseModel):
        app_id: Literal["example/model"]
        prompt: Literal["Draw a tree", "Draw a flower"]
        image_url: Literal["https://example.com/reference", "https://example.com/other"]
        count: Literal[3, 5]
        modes: list[Literal["fast", "quality"]] = Field(min_length=1)

    payload = safe_yaml.load(_build_schema_example_yaml(ChoicesConfig, "example/model"))

    assert payload["parameters"] == {
        "prompt": "Draw a tree",
        "image_url": "https://example.com/reference",
        "count": 3,
        "modes": ["fast"],
    }
    ChoicesConfig.model_validate({"app_id": payload["app_id"], **payload["parameters"]})


def test_schema_prints_commented_job_config_yaml_example() -> None:
    result = runner.invoke(app, ["schema", "openai/gpt-image-2"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert set(payload) == {
        "app_id",
        "parameters",
        "output_dir",
        "slug",
        "version",
        "iterations",
        "max_concurrency",
    }
    assert payload["app_id"] == "openai/gpt-image-2"
    assert isinstance(payload["parameters"], dict)
    assert "prompt" in payload["parameters"]
    assert payload["slug"] == "<kebab-case-output-slug>"
    assert payload["version"] == 1
    assert payload["iterations"] == 1
    assert payload["max_concurrency"] == 8
    assert any(line.lstrip().startswith("# ") for line in result.stdout.splitlines())
    assert "results:" not in result.stdout
    assert "uploads:" not in result.stdout
    assert "output_expiration_seconds:" not in result.stdout
    assert "upload_reuse_window_seconds:" not in result.stdout


@pytest.mark.parametrize(
    "app_id",
    [
        "fal-ai/bytedance/seedream/v4.5/edit",
        "fal-ai/bytedance/seedream/v4.5/text-to-image",
    ],
)
def test_schema_prints_seedream_v45_yaml_example(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"]["image_size"] is not None


@pytest.mark.parametrize(
    "app_id",
    [
        "fal-ai/bytedance/seedream/v5/lite/edit",
        "fal-ai/bytedance/seedream/v5/lite/text-to-image",
    ],
)
def test_schema_prints_seedream_v5_lite_yaml_example(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"]["image_size"] == "auto_2K"
    parameters = {**payload["parameters"], "image_size": "auto_3K"}
    assert validate_parameters(app_id, parameters).image_size == "auto_3K"


def test_schema_prints_seedream_v5_lite_text_to_image_byteplus_urls_example() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/bytedance/seedream/v5/lite/text-to-image"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["return_byteplus_urls"] is False


def test_schema_prints_seedream_v5_lite_edit_image_urls_example() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/bytedance/seedream/v5/lite/edit"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["image_urls"] == ["https://example.com/input"]
    assert "return_byteplus_urls" not in payload["parameters"]


def test_schema_prints_valid_flux_3_keyframes_parameters() -> None:
    result = runner.invoke(app, ["schema", "blackforestlabs/flux-3/keyframes-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    config = Flux3KeyframesToVideoConfig.model_validate(
        {"app_id": payload["app_id"], **payload["parameters"]}
    )
    assert [keyframe.model_dump() for keyframe in config.keyframes] == [
        {"image_url": "https://example.com/input", "frame_index": 1}
    ]


def test_schema_prints_flux_3_extend_video_prompt_contract() -> None:
    result = runner.invoke(app, ["schema", "blackforestlabs/flux-3/extend-video"])

    assert result.exit_code == 0
    assert (
        "# The text prompt describing how the video continues from the source clip's final frames."
        in result.stdout
    )


def test_schema_exits_one_for_unknown_app_id() -> None:
    result = runner.invoke(app, ["schema", "unknown/model"])

    assert result.exit_code == 1
    assert "Unknown app_id: unknown/model" in result.stderr


def test_seedance2_duration_description_enumerates_allowed_values() -> None:
    result = runner.invoke(app, ["schema", "bytedance/seedance-2.0/image-to-video"])

    assert result.exit_code == 0
    assert (
        "Allowed values: '4', '5', '6', '7', '8', '9', '10', '11', '12', "
        "'13', '14', '15' (string) or 'auto' (string)" in result.stdout
    )


def test_happy_horse_duration_description_enumerates_allowed_values() -> None:
    result = runner.invoke(app, ["schema", "alibaba/happy-horse/image-to-video"])

    assert result.exit_code == 0
    assert "Allowed values: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 (int)" in result.stdout


def test_kling_v3_pro_duration_description_enumerates_allowed_values() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/kling-video/v3/pro/text-to-video"])

    assert result.exit_code == 0
    assert (
        "Allowed values: '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', "
        "'13', '14', '15' (string)" in result.stdout
    )


def test_kling_o3_pro_duration_description_enumerates_allowed_values() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/kling-video/o3/pro/text-to-video"])

    assert result.exit_code == 0
    assert (
        "Allowed values: '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', "
        "'13', '14', '15' (string)" in result.stdout
    )


def test_kling_v3_shot_duration_description_enumerates_allowed_values() -> None:
    description = KlingV3MultiPromptElement.model_fields["duration"].description
    assert description is not None
    assert (
        "Allowed values: '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', "
        "'11', '12', '13', '14', '15' (string)" in description
    )


def test_kling_o3_shot_duration_description_enumerates_allowed_values() -> None:
    description = KlingO3MultiPromptElement.model_fields["duration"].description
    assert description is not None
    assert (
        "Allowed values: '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', "
        "'11', '12', '13', '14', '15' (string)" in description
    )


@pytest.mark.parametrize(
    "app_id",
    [
        "fal-ai/veo3.1",
        "fal-ai/veo3.1/image-to-video",
        "fal-ai/veo3.1/first-last-frame-to-video",
        "fal-ai/veo3.1/reference-to-video",
    ],
)
def test_schema_prints_veo3_1_yaml_example(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["duration"] == "8s"
    assert payload["parameters"]["resolution"] == "720p"
    assert payload["parameters"]["generate_audio"] is True
    assert payload["parameters"]["safety_tolerance"] == "4"


def test_schema_prints_veo3_1_text_to_video_defaults() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/veo3.1"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["aspect_ratio"] == "16:9"
    assert payload["parameters"]["auto_fix"] is True
    assert "image_url" not in payload["parameters"]
    assert payload["parameters"]["duration"] == "8s"
    assert "The duration of the generated video." in result.stdout


def test_schema_prints_veo3_1_image_to_video_defaults() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/veo3.1/image-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["aspect_ratio"] == "auto"
    assert payload["parameters"]["auto_fix"] is False
    assert payload["parameters"]["image_url"] == "https://example.com/input"


def test_schema_prints_veo3_1_first_last_frame_to_video_required_urls() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/veo3.1/first-last-frame-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["first_frame_url"] == "https://example.com/input"
    assert payload["parameters"]["last_frame_url"] == "https://example.com/input"


def test_schema_prints_veo3_1_reference_to_video_fields() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/veo3.1/reference-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["aspect_ratio"] == "16:9"
    assert payload["parameters"]["image_urls"] == ["https://example.com/input"]
    assert "negative_prompt" not in payload["parameters"]
    assert "seed" not in payload["parameters"]


@pytest.mark.parametrize(
    "app_id",
    [
        "fal-ai/vidu/q3/text-to-video",
        "fal-ai/vidu/q3/image-to-video",
        "fal-ai/vidu/q3/reference-to-video",
        "fal-ai/vidu/q3/reference-to-video/mix",
    ],
)
def test_schema_prints_vidu_q3_yaml_example(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"]["duration"] == 5
    assert payload["parameters"]["seed"] is None
    assert payload["parameters"]["resolution"] == "720p"
    assert payload["parameters"]["audio"] is True
    assert "Allowed values: '360p', '540p', '720p', '1080p' (string)." in result.stdout


def test_schema_prints_vidu_q3_text_to_video_defaults() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/vidu/q3/text-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["aspect_ratio"] == "16:9"
    assert "image_url" not in payload["parameters"]
    assert "reference_image_urls" not in payload["parameters"]


def test_schema_prints_vidu_q3_image_to_video_fields() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/vidu/q3/image-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["prompt"] == ""
    assert payload["parameters"]["image_url"] == "https://example.com/input"
    assert payload["parameters"]["end_image_url"] is None
    assert "aspect_ratio" not in payload["parameters"]


def test_schema_prints_vidu_q3_reference_to_video_fields() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/vidu/q3/reference-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["reference_image_urls"] == ["https://example.com/input"]
    assert payload["parameters"]["aspect_ratio"] == "16:9"
    assert "image_url" not in payload["parameters"]


@pytest.mark.parametrize(
    "app_id",
    [
        "luma/agent/ray/v3.2/text-to-video",
        "luma/agent/ray/v3.2/image-to-video",
        "luma/agent/ray/v3.2/video-to-video",
        "luma/agent/ray/v3.2/reframe",
    ],
)
def test_schema_prints_luma_ray_3_2_yaml_example(app_id: str) -> None:
    result = runner.invoke(app, ["schema", app_id])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["app_id"] == app_id
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["resolution"] == "540p"
    assert "Allowed values: '540p', '720p', '1080p' (string)." in result.stdout


def test_schema_prints_luma_ray_3_2_text_to_video_fields() -> None:
    result = runner.invoke(app, ["schema", "luma/agent/ray/v3.2/text-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["aspect_ratio"] == "16:9"
    assert payload["parameters"]["duration"] == "5s"
    assert payload["parameters"]["loop"] is False
    assert payload["parameters"]["hdr"] is False
    assert payload["parameters"]["exr_export"] is False
    assert "reference_image_urls" not in payload["parameters"]


def test_schema_prints_luma_ray_3_2_image_to_video_fields() -> None:
    result = runner.invoke(app, ["schema", "luma/agent/ray/v3.2/image-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["image_url"] == "https://example.com/input"
    assert payload["parameters"]["end_image_url"] is None
    assert payload["parameters"]["duration"] == "5s"
    assert payload["parameters"]["keyframes"] is None
    assert payload["parameters"]["keyframe_indexes"] is None


def test_schema_prints_luma_ray_3_2_video_to_video_fields() -> None:
    result = runner.invoke(app, ["schema", "luma/agent/ray/v3.2/video-to-video"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["video_url"] == "https://example.com/input"
    assert payload["parameters"]["start_image_url"] is None
    assert payload["parameters"]["edit_strength"] is None
    assert payload["parameters"]["auto_controls"] is False
    assert payload["parameters"]["controls"] is None


def test_schema_prints_luma_ray_3_2_reframe_fields() -> None:
    result = runner.invoke(app, ["schema", "luma/agent/ray/v3.2/reframe"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["video_url"] == "https://example.com/input"
    assert payload["parameters"]["aspect_ratio"] == "3:4"
    assert payload["parameters"]["source_position"] is None


def test_schema_prints_vidu_q3_reference_to_video_mix_fields() -> None:
    result = runner.invoke(app, ["schema", "fal-ai/vidu/q3/reference-to-video/mix"])

    assert result.exit_code == 0
    payload = safe_yaml.load(result.stdout)
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["reference_image_urls"] == ["https://example.com/input"]
    assert payload["parameters"]["aspect_ratio"] == "16:9"
    assert "image_url" not in payload["parameters"]
