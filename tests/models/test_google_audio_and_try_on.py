from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML
from typer.testing import CliRunner

from falx.cli import app
from falx.models import SUPPORTED_APP_IDS, FalConfig, config_class_for_app_id

GEMINI_TTS = "fal-ai/gemini-tts"
GEMINI_31 = "fal-ai/gemini-3.1-flash-tts"
GEMINI_38 = (
    "google/gemini-3.8-flash-tts",
    "google/gemini-3.8-flash-lite-tts",
)
LYRIA = ("fal-ai/lyria2", "fal-ai/lyria3", "fal-ai/lyria3/pro", "google/lyria-3.5")
TRY_ON = "google/virtual-try-on"
APP_IDS = (GEMINI_TTS, GEMINI_31, *GEMINI_38, *LYRIA, TRY_ON)
PROMPT = "A warm welcome."
SPEAKERS = [
    {"speaker_id": "Alice", "voice": "Kore"},
    {"speaker_id": "Bob", "voice": "Puck"},
]


def validate(app_id: str, **parameters: object):
    assert config_class_for_app_id(app_id) is not None
    return TypeAdapter(FalConfig).validate_python({"app_id": app_id, **parameters})


@pytest.mark.parametrize("app_id", APP_IDS)
def test_google_audio_and_try_on_endpoints_are_registered(app_id: str) -> None:
    assert app_id in SUPPORTED_APP_IDS
    assert config_class_for_app_id(app_id) is not None


@pytest.mark.parametrize("app_id", (GEMINI_TTS, GEMINI_31, *GEMINI_38))
def test_gemini_tts_accepts_single_speaker_defaults(app_id: str) -> None:
    config = validate(app_id, prompt=PROMPT)
    expected = {
        "app_id": app_id,
        "prompt": PROMPT,
        "style_instructions": None,
        "voice": "Kore",
        "speakers": None,
        "enable_safety_checker": True,
    }
    if app_id in GEMINI_38:
        expected["turns"] = None
    else:
        expected.update(language_code=None, temperature=1, output_format="mp3")
    if app_id == GEMINI_TTS:
        expected["model"] = "gemini-2.5-flash-tts"
    assert config.model_dump() == expected


@pytest.mark.parametrize("app_id", (GEMINI_TTS, GEMINI_31))
@pytest.mark.parametrize("temperature", [0, 2])
@pytest.mark.parametrize("output_format", ["wav", "mp3", "ogg_opus"])
def test_gemini_tts_accepts_prompt_style_and_temperature_boundaries(
    app_id: str, temperature: int, output_format: str
) -> None:
    config = validate(
        app_id,
        prompt="x" * 50000,
        style_instructions="x" * 4000,
        voice="Zubenelgenubi",
        language_code="Japanese (Japan)",
        speakers=SPEAKERS * 5,
        temperature=temperature,
        output_format=output_format,
        enable_safety_checker=False,
    )
    assert len(config.prompt) == 50000
    assert len(config.style_instructions) == 4000
    assert config.temperature == temperature
    assert config.output_format == output_format
    assert config.model_dump()["speakers"] == SPEAKERS * 5


@pytest.mark.parametrize("model", ["gemini-2.5-flash-tts", "gemini-2.5-pro-tts"])
def test_gemini_tts_accepts_both_model_choices(model: str) -> None:
    assert validate(GEMINI_TTS, prompt="x", model=model).model == model


@pytest.mark.parametrize("app_id", (GEMINI_TTS, GEMINI_31))
@pytest.mark.parametrize(
    ("parameters", "field"),
    [
        ({}, "prompt"),
        ({"prompt": None}, "prompt"),
        ({"prompt": ""}, "prompt"),
        ({"prompt": "x" * 50001}, "prompt"),
        ({"prompt": "x", "style_instructions": "x" * 4001}, "style_instructions"),
        ({"prompt": "x", "temperature": -0.01}, "temperature"),
        ({"prompt": "x", "temperature": 2.01}, "temperature"),
        ({"prompt": "x", "language_code": "xx"}, "language_code"),
        ({"prompt": "x", "voice": "unknown"}, "voice"),
        ({"prompt": "x", "output_format": "aac"}, "output_format"),
        ({"prompt": "x", "speakers": SPEAKERS[:1]}, "speakers"),
        ({"prompt": "x", "speakers": SPEAKERS * 6}, "speakers"),
        (
            {"prompt": "x", "speakers": [*SPEAKERS[:1], {"voice": "Kore"}]},
            "speaker_id",
        ),
        (
            {"prompt": "x", "speakers": [{"speaker_id": "Alice"}, SPEAKERS[1]]},
            "voice",
        ),
        (
            {
                "prompt": "x",
                "speakers": [{"speaker_id": "bad alias", "voice": "Kore"}, SPEAKERS[1]],
            },
            "speaker_id",
        ),
        (
            {
                "prompt": "x",
                "speakers": [{"speaker_id": "Alice", "voice": "unknown"}, SPEAKERS[1]],
            },
            "voice",
        ),
    ],
)
def test_gemini_tts_rejects_invalid_speech_inputs(
    app_id: str, parameters: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate(app_id, **parameters)


def test_gemini_tts_rejects_empty_speaker_list_but_31_accepts_it() -> None:
    with pytest.raises(ValidationError, match="speakers"):
        validate(GEMINI_TTS, prompt="x", speakers=[])
    assert validate(GEMINI_31, prompt="x", speakers=[]).speakers == []


@pytest.mark.parametrize("app_id", GEMINI_38)
def test_gemini_38_accepts_dialogue_and_preserves_turns(app_id: str) -> None:
    turns = [
        {"speaker_id": "Alice", "text": "Hello!", "style_instructions": "cheerful"},
        {"speaker_id": "Bob", "text": "Welcome!"},
    ]
    config = validate(app_id, speakers=SPEAKERS, turns=turns)
    assert config.model_dump()["speakers"] == SPEAKERS
    assert config.model_dump()["turns"] == [
        turns[0],
        {**turns[1], "style_instructions": None},
    ]


@pytest.mark.parametrize("app_id", GEMINI_38)
@pytest.mark.parametrize(
    ("parameters", "field"),
    [
        ({"prompt": "x", "voice": "unknown"}, "voice"),
        ({"speakers": SPEAKERS[:1]}, "speakers"),
        ({"speakers": SPEAKERS + SPEAKERS[:1]}, "speakers"),
        ({"speakers": SPEAKERS, "turns": []}, "turns"),
        (
            {
                "speakers": [{"speaker_id": "", "voice": "Kore"}, SPEAKERS[1]],
                "turns": [{"speaker_id": "Bob", "text": "Hello"}],
            },
            "speaker_id",
        ),
        (
            {"speakers": SPEAKERS, "turns": [{"speaker_id": "Alice", "text": ""}]},
            "text",
        ),
        (
            {"speakers": SPEAKERS, "turns": [{"speaker_id": "", "text": "Hello"}]},
            "speaker_id",
        ),
        ({"speakers": SPEAKERS, "turns": [{"speaker_id": "Alice"}]}, "text"),
    ],
)
def test_gemini_38_rejects_invalid_dialogue_fields(
    app_id: str, parameters: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate(app_id, **parameters)


@pytest.mark.parametrize("app_id", GEMINI_38)
@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"prompt": None},
        {"speakers": SPEAKERS},
        {"turns": [{"speaker_id": "Alice", "text": "Hello"}]},
        {"prompt": "Hello", "speakers": SPEAKERS},
        {
            "speakers": [SPEAKERS[0], SPEAKERS[0]],
            "turns": [{"speaker_id": "Alice", "text": "Hello"}],
        },
        {"speakers": SPEAKERS, "turns": [{"speaker_id": "Charlie", "text": "Hello"}]},
    ],
)
def test_gemini_38_requires_speech_or_complete_dialogue(
    app_id: str, parameters: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        validate(app_id, **parameters)


@pytest.mark.parametrize("app_id", GEMINI_38)
def test_gemini_38_accepts_prompt_alongside_complete_dialogue(app_id: str) -> None:
    turns = [{"speaker_id": "Alice", "text": "Hello"}]
    config = validate(app_id, prompt="Hello", speakers=SPEAKERS, turns=turns)
    assert config.prompt == "Hello"
    assert config.turns[0].speaker_id == "Alice"


@pytest.mark.parametrize("app_id", GEMINI_38)
def test_gemini_38_does_not_add_unpublished_string_length_limits(app_id: str) -> None:
    config = validate(app_id, prompt="", style_instructions="x" * 5001)
    assert config.prompt == ""
    assert len(config.style_instructions) == 5001


@pytest.mark.parametrize("app_id", LYRIA)
def test_lyria_accepts_schema_defaults(app_id: str) -> None:
    config = validate(app_id, prompt=PROMPT)
    expected = {
        "app_id": app_id,
        "prompt": PROMPT,
        "negative_prompt": "low quality" if app_id == "fal-ai/lyria2" else "",
        "enable_safety_checker": True,
    }
    expected["seed" if app_id == "fal-ai/lyria2" else "image_url"] = None
    assert config.model_dump() == expected


@pytest.mark.parametrize("app_id", LYRIA)
@pytest.mark.parametrize("use_maximum_length", [False, True])
def test_lyria_accepts_prompt_boundaries_and_optional_fields(
    app_id: str, use_maximum_length: bool
) -> None:
    maximum = 2000 if app_id == "fal-ai/lyria2" else 5000
    parameters = {
        "prompt": "x" * (maximum if use_maximum_length else 1),
        "negative_prompt": "vocals",
        "enable_safety_checker": False,
    }
    if app_id == "fal-ai/lyria2":
        parameters["seed"] = 42
    else:
        parameters["image_url"] = "https://example.com/inspiration.png"
    config = validate(app_id, **parameters)
    assert config.model_dump() == {"app_id": app_id, **parameters}


@pytest.mark.parametrize("app_id", LYRIA)
@pytest.mark.parametrize("prompt", [None, "", "x" * 5001])
def test_lyria_rejects_invalid_prompt(app_id: str, prompt: str | None) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validate(app_id, prompt=prompt)


def test_lyria2_rejects_prompt_above_its_own_limit() -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validate("fal-ai/lyria2", prompt="x" * 2001)


@pytest.mark.parametrize("app_id", LYRIA)
def test_lyria_requires_prompt(app_id: str) -> None:
    with pytest.raises(ValidationError, match="prompt"):
        validate(app_id)


@pytest.mark.parametrize("num_images", [1, 4])
def test_virtual_try_on_accepts_two_images_and_sample_boundaries(num_images: int) -> None:
    config = validate(
        TRY_ON,
        person_image_url="https://example.com/person.png",
        product_image_url="https://example.com/product.png",
        num_images=num_images,
        enable_safety_checker=False,
    )
    assert config.model_dump() == {
        "app_id": TRY_ON,
        "person_image_url": "https://example.com/person.png",
        "product_image_url": "https://example.com/product.png",
        "num_images": num_images,
        "enable_safety_checker": False,
    }


def test_virtual_try_on_uses_one_image_and_safety_checker_by_default() -> None:
    config = validate(TRY_ON, person_image_url="person", product_image_url="product")
    assert config.num_images == 1
    assert config.enable_safety_checker is True


@pytest.mark.parametrize("field", ["person_image_url", "product_image_url"])
def test_virtual_try_on_requires_both_input_images(field: str) -> None:
    parameters = {"person_image_url": "person", "product_image_url": "product"}
    del parameters[field]
    with pytest.raises(ValidationError, match=field):
        validate(TRY_ON, **parameters)


@pytest.mark.parametrize("num_images", [0, 5])
def test_virtual_try_on_rejects_invalid_sample_count(num_images: int) -> None:
    with pytest.raises(ValidationError, match="num_images"):
        validate(
            TRY_ON, person_image_url="person", product_image_url="product", num_images=num_images
        )


@pytest.mark.parametrize("app_id", APP_IDS)
def test_google_audio_and_try_on_reject_unknown_parameters(app_id: str) -> None:
    parameters = (
        {"person_image_url": "person", "product_image_url": "product"}
        if app_id == TRY_ON
        else {"prompt": PROMPT}
    )
    with pytest.raises(ValidationError, match="unknown_parameter"):
        validate(app_id, **parameters, unknown_parameter=True)


def test_models_command_lists_google_audio_and_try_on() -> None:
    result = CliRunner().invoke(app, ["models"])
    assert result.exit_code == 0
    assert set(APP_IDS) <= set(result.stdout.splitlines())


@pytest.mark.parametrize("app_id", APP_IDS)
def test_schema_command_prints_google_audio_and_try_on_parameters(app_id: str) -> None:
    result = CliRunner().invoke(app, ["schema", app_id])
    assert result.exit_code == 0
    payload = YAML(typ="safe").load(result.stdout)
    assert payload["app_id"] == app_id
    assert "app_id" not in payload["parameters"]
    if app_id == TRY_ON:
        assert payload["parameters"]["person_image_url"] == "https://example.com/input"
        assert payload["parameters"]["product_image_url"] == "https://example.com/input"
    elif app_id not in GEMINI_38:
        assert payload["parameters"]["prompt"] == "<your prompt here>"
    assert payload["parameters"]["enable_safety_checker"] is True
