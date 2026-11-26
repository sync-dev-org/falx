from __future__ import annotations

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import (
    SUPPORTED_APP_IDS,
    config_class_for_app_id,
    validate_parameters,
)

FAMILIES = {
    "classic": ("fal-ai/nano-banana", "fal-ai/gemini-25-flash-image"),
    "pro": ("fal-ai/nano-banana-pro", "fal-ai/gemini-3-pro-image-preview"),
    "flash": ("fal-ai/nano-banana-2", "fal-ai/gemini-3.1-flash-image-preview"),
    "lite": ("google/nano-banana-lite",),
}
ENDPOINTS = [
    (family, endpoint + suffix)
    for family, endpoints in FAMILIES.items()
    for endpoint in endpoints
    for suffix in ("", "/edit")
]
NATIVE_ENDPOINTS = [endpoint for family, endpoint in ENDPOINTS if family in ("pro", "flash")]
runner = CliRunner()


def parameters_for(endpoint: str) -> dict[str, object]:
    parameters: dict[str, object] = {"prompt": "a cat on a mat"}
    if endpoint.endswith("/edit"):
        parameters["image_urls"] = ["https://example.com/input.png"]
    return parameters


@pytest.mark.parametrize(("family", "endpoint"), ENDPOINTS)
def test_nano_banana_endpoints_validate_parameters_and_preserve_defaults(
    family: str, endpoint: str
) -> None:
    assert endpoint in SUPPORTED_APP_IDS
    config = validate_parameters(endpoint, parameters_for(endpoint))
    assert config is not None
    assert config.app_id == endpoint
    assert config.random_seed_field == "seed"
    expected = {
        "app_id": endpoint,
        **parameters_for(endpoint),
        "num_images": 1,
        "seed": None,
        "output_format": "png",
        "safety_tolerance": "4",
        "sync_mode": False,
        "limit_generations": True,
        "aspect_ratio": (
            "1:1" if family in ("classic", "pro") and not endpoint.endswith("/edit") else "auto"
        ),
    }
    if family != "classic":
        expected.update(system_prompt="", thinking_level=None)
    if family in ("pro", "flash"):
        expected.update(
            resolution="1K",
            return_history=False,
            include_thoughts=None,
            temperature=None,
            top_p=None,
            max_output_tokens=None,
            history=[],
            context=[],
            enable_web_search=False,
        )
    if family == "flash":
        expected["enable_image_search"] = False
        if endpoint.endswith("/edit"):
            expected.update(video_url=None, audio_url=None, pdf_url=None)
    assert config.model_dump() == expected


@pytest.mark.parametrize(("family", "endpoints"), list(FAMILIES.items())[:3])
@pytest.mark.parametrize("suffix", ["", "/edit"])
def test_nano_banana_aliases_share_the_matching_parameter_class(
    family: str, endpoints: tuple[str, ...], suffix: str
) -> None:
    assert config_class_for_app_id(endpoints[0] + suffix) is not None
    assert config_class_for_app_id(endpoints[0] + suffix) is config_class_for_app_id(
        endpoints[1] + suffix
    )


@pytest.mark.parametrize(("family", "endpoint"), ENDPOINTS)
def test_nano_banana_rejects_missing_prompt(family: str, endpoint: str) -> None:
    parameters = parameters_for(endpoint)
    del parameters["prompt"]
    with pytest.raises(ValidationError, match="prompt"):
        validate_parameters(endpoint, parameters)


@pytest.mark.parametrize("endpoint", [endpoints[0] for endpoints in FAMILIES.values()])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "hi"),
        ("prompt", "a" * 50001),
        ("num_images", 0),
        ("num_images", 5),
        ("output_format", "gif"),
        ("safety_tolerance", "0"),
        ("safety_tolerance", "7"),
        ("aspect_ratio", "7:3"),
        ("unknown_option", True),
    ],
)
def test_nano_banana_rejects_invalid_shared_parameters(
    endpoint: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(endpoint, {"prompt": "a cat", field: value})


@pytest.mark.parametrize("endpoint", [endpoints[0] for endpoints in FAMILIES.values()])
@pytest.mark.parametrize("prompt", ["cat", "a" * 50000])
@pytest.mark.parametrize("num_images", [1, 4])
def test_nano_banana_accepts_prompt_and_image_count_boundaries(
    endpoint: str, prompt: str, num_images: int
) -> None:
    config = validate_parameters(endpoint, {"prompt": prompt, "num_images": num_images})
    assert config is not None
    assert config.prompt == prompt
    assert config.num_images == num_images


@pytest.mark.parametrize("endpoint", NATIVE_ENDPOINTS)
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("temperature", -0.01),
        ("temperature", 2.01),
        ("top_p", -0.01),
        ("top_p", 1.01),
        ("max_output_tokens", 0),
        ("max_output_tokens", 32769),
        ("system_prompt", "a" * 50001),
        ("thinking_level", "medium"),
        ("resolution", "8K"),
    ],
)
def test_nano_banana_native_controls_reject_out_of_range_values(
    endpoint: str, field: str, value: object
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_parameters(endpoint, {**parameters_for(endpoint), field: value})


@pytest.mark.parametrize("endpoint", NATIVE_ENDPOINTS)
@pytest.mark.parametrize("upper", [False, True])
def test_nano_banana_native_controls_accept_sampling_boundaries(endpoint: str, upper: bool) -> None:
    values = {
        "temperature": 2.0 if upper else 0.0,
        "top_p": 1.0 if upper else 0.0,
        "max_output_tokens": 32768 if upper else 1,
        "system_prompt": "a" * 50000,
        "include_thoughts": False,
        "return_history": True,
    }
    config = validate_parameters(endpoint, {**parameters_for(endpoint), **values})
    assert config is not None
    assert all(config.model_dump()[field] == value for field, value in values.items())


@pytest.mark.parametrize("endpoint", NATIVE_ENDPOINTS)
def test_nano_banana_preserves_native_context_and_conversation_signatures(endpoint: str) -> None:
    parts = [
        {"type": "text", "text": "original prompt", "thought": True},
        {"type": "image", "image_url": "data:image/png;base64,AAAA"},
        {
            "type": "document",
            "file_url": "https://example.com/a.pdf",
            "mime_type": "application/pdf",
        },
        {"type": "signature", "thought_signature": "opaque-provider-signature"},
    ]
    if "nano-banana-2" in endpoint or "3.1-flash" in endpoint:
        parts.append({"type": "video", "video_url": "https://example.com/input.mp4"})
    history_parts = [*parts]
    if "nano-banana-2" in endpoint or "3.1-flash" in endpoint:
        history_parts.append({"type": "audio", "audio_url": "https://example.com/input.mp3"})
    history = [{"role": "model", "parts": history_parts}]
    config = validate_parameters(
        endpoint, {**parameters_for(endpoint), "context": parts, "history": history}
    )
    assert config is not None
    dumped = config.model_dump(exclude_unset=True)
    assert dumped["context"] == parts
    assert dumped["history"] == history


@pytest.mark.parametrize("endpoint", ["fal-ai/nano-banana-pro", "fal-ai/nano-banana-2"])
@pytest.mark.parametrize(
    ("field", "value", "needle"),
    [
        ("history", [{"role": "assistant", "parts": [{"type": "text", "text": "hi"}]}], "role"),
        ("history", [{"role": "user", "parts": []}], "parts"),
        ("context", [{"type": "image"}], "image_url"),
        ("context", [{"type": "text"}], "text"),
        (
            "context",
            [{"type": "document", "file_url": "a.pdf", "mime_type": "image/png"}],
            "mime_type",
        ),
        ("context", [{"type": "signature", "thought_signature": ""}], "thought_signature"),
        ("context", [{"type": "text", "text": "hi", "thought_signature": ""}], "thought_signature"),
        ("context", [{"type": "audio", "audio_url": "input.mp3"}], "context"),
        ("context", [{"type": "unknown"}], "context"),
    ],
)
def test_nano_banana_rejects_invalid_native_conversation_parts(
    endpoint: str, field: str, value: object, needle: str
) -> None:
    with pytest.raises(ValidationError, match=needle):
        validate_parameters(endpoint, {"prompt": "a cat", field: value})


@pytest.mark.parametrize("endpoint", FAMILIES["pro"])
def test_nano_banana_pro_rejects_flash_only_controls(endpoint: str) -> None:
    for field, value in [
        ("resolution", "0.5K"),
        ("thinking_level", "minimal"),
        ("enable_image_search", True),
    ]:
        with pytest.raises(ValidationError, match=field):
            validate_parameters(endpoint, {"prompt": "a cat", field: value})
    with pytest.raises(ValidationError, match="context"):
        validate_parameters(
            endpoint,
            {"prompt": "a cat", "context": [{"type": "video", "video_url": "input.mp4"}]},
        )


@pytest.mark.parametrize("endpoint", FAMILIES["flash"])
def test_nano_banana_flash_accepts_image_search_and_half_k_resolution(endpoint: str) -> None:
    config = validate_parameters(
        endpoint,
        {
            "prompt": "a cat",
            "resolution": "0.5K",
            "enable_image_search": True,
            "thinking_level": "minimal",
        },
    )
    assert config is not None
    assert config.enable_image_search is True
    assert config.resolution == "0.5K"
    assert config.thinking_level == "minimal"


def test_nano_banana_lite_exposes_its_controls_without_pro_only_fields() -> None:
    config = validate_parameters(
        "google/nano-banana-lite",
        {
            "prompt": "a cat",
            "aspect_ratio": "8:1",
            "thinking_level": "high",
            "system_prompt": "a" * 50000,
        },
    )
    assert config is not None
    assert config.thinking_level == "high"
    for field, value in [("resolution", "1K"), ("enable_web_search", True), ("history", [])]:
        with pytest.raises(ValidationError, match=field):
            validate_parameters("google/nano-banana-lite", {"prompt": "a cat", field: value})
    with pytest.raises(ValidationError, match="system_prompt"):
        validate_parameters(
            "google/nano-banana-lite", {"prompt": "a cat", "system_prompt": "a" * 50001}
        )


def test_nano_banana_classic_edit_requires_image_urls() -> None:
    for endpoint in FAMILIES["classic"]:
        with pytest.raises(ValidationError, match="image_urls"):
            validate_parameters(endpoint + "/edit", {"prompt": "a cat"})
        config = validate_parameters(endpoint + "/edit", {"prompt": "a cat", "image_urls": []})
        assert config is not None
        assert config.image_urls == []


@pytest.mark.parametrize(
    "endpoint",
    [
        endpoint
        for family, endpoint in ENDPOINTS
        if family != "classic" and endpoint.endswith("/edit")
    ],
)
def test_nano_banana_edit_accepts_optional_image_inputs(endpoint: str) -> None:
    for parameters in [{"prompt": "edit this"}, {"prompt": "edit this", "image_urls": []}]:
        config = validate_parameters(endpoint, parameters)
        assert config is not None
        assert config.image_urls == []


def test_models_command_lists_all_nano_banana_endpoints() -> None:
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert {endpoint for _, endpoint in ENDPOINTS} <= set(result.stdout.splitlines())


@pytest.mark.parametrize(("family", "endpoint"), ENDPOINTS)
def test_schema_command_prints_nano_banana_job_yaml(family: str, endpoint: str) -> None:
    result = runner.invoke(app, ["schema", endpoint])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == endpoint
    assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["num_images"] == 1
    assert payload["parameters"]["seed"] is None
    if family in ("pro", "flash"):
        assert payload["parameters"]["history"] == []
        assert payload["parameters"]["context"] == []
        assert payload["parameters"]["max_output_tokens"] is None
