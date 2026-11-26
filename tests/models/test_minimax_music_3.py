from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import MinimaxMusic3Config

APP_ID = "minimax/music-3"


def test_minimax_music_3_accepts_schema_defaults() -> None:
    config = MinimaxMusic3Config(
        app_id=APP_ID,
        prompt="Acoustic pop with warm vocals.",
        lyrics="[verse]\nMorning light",
    )

    assert config.model_dump() == {
        "enable_safety_checker": True,
        "app_id": APP_ID,
        "prompt": "Acoustic pop with warm vocals.",
        "lyrics": "[verse]\nMorning light",
        "duration": 60.0,
        "seed": None,
        "num_inference_steps": 30,
        "guidance_scale": 1.7,
    }


def test_minimax_music_3_accepts_all_fields_at_boundaries() -> None:
    config = MinimaxMusic3Config(
        app_id=APP_ID,
        prompt="Instrumental ambient soundscape.",
        lyrics="",
        duration=300,
        seed=42,
        num_inference_steps=100,
        guidance_scale=20,
    )

    assert config.model_dump() == {
        "enable_safety_checker": True,
        "app_id": APP_ID,
        "prompt": "Instrumental ambient soundscape.",
        "lyrics": "",
        "duration": 300.0,
        "seed": 42,
        "num_inference_steps": 100,
        "guidance_scale": 20.0,
    }


def test_minimax_music_3_schema_matches_openapi_contract() -> None:
    schema = MinimaxMusic3Config.model_json_schema()

    assert schema["required"] == ["app_id", "prompt", "lyrics"]
    assert schema["properties"]["duration"] == {
        "default": 60.0,
        "description": (
            "Upper bound on the generated audio length in seconds. The model may stop "
            "earlier; the actual duration is returned in the output."
        ),
        "maximum": 300,
        "minimum": 1,
        "title": "Duration",
        "type": "number",
    }
    assert schema["properties"]["num_inference_steps"]["default"] == 30
    assert schema["properties"]["num_inference_steps"]["minimum"] == 1
    assert schema["properties"]["num_inference_steps"]["maximum"] == 100
    assert schema["properties"]["guidance_scale"]["default"] == 1.7
    assert schema["properties"]["guidance_scale"]["minimum"] == 0
    assert schema["properties"]["guidance_scale"]["maximum"] == 20


def test_minimax_music_3_accepts_empty_prompt_and_lyrics() -> None:
    config = MinimaxMusic3Config(app_id=APP_ID, prompt="", lyrics="")

    assert config.prompt == ""
    assert config.lyrics == ""


@pytest.mark.parametrize("duration", [1, 300])
def test_minimax_music_3_accepts_duration_boundaries(duration: int) -> None:
    config = MinimaxMusic3Config(
        app_id=APP_ID,
        prompt="Ambient.",
        lyrics="Instrumental",
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize("num_inference_steps", [1, 100])
def test_minimax_music_3_accepts_inference_step_boundaries(
    num_inference_steps: int,
) -> None:
    config = MinimaxMusic3Config(
        app_id=APP_ID,
        prompt="Ambient.",
        lyrics="Instrumental",
        num_inference_steps=num_inference_steps,
    )

    assert config.num_inference_steps == num_inference_steps


@pytest.mark.parametrize("guidance_scale", [0, 20])
def test_minimax_music_3_accepts_guidance_scale_boundaries(
    guidance_scale: int,
) -> None:
    config = MinimaxMusic3Config(
        app_id=APP_ID,
        prompt="Ambient.",
        lyrics="Instrumental",
        guidance_scale=guidance_scale,
    )

    assert config.guidance_scale == guidance_scale


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        ({"app_id": APP_ID, "lyrics": "Instrumental"}, "prompt"),
        ({"app_id": APP_ID, "prompt": "Ambient."}, "lyrics"),
        ({"app_id": APP_ID, "prompt": None, "lyrics": "Instrumental"}, "prompt"),
        ({"app_id": APP_ID, "prompt": "Ambient.", "lyrics": None}, "lyrics"),
        (
            {"app_id": APP_ID, "prompt": "Ambient.", "lyrics": "Instrumental", "duration": 0},
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Ambient.",
                "lyrics": "Instrumental",
                "duration": 301,
            },
            "duration",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Ambient.",
                "lyrics": "Instrumental",
                "num_inference_steps": 0,
            },
            "num_inference_steps",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Ambient.",
                "lyrics": "Instrumental",
                "num_inference_steps": 101,
            },
            "num_inference_steps",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Ambient.",
                "lyrics": "Instrumental",
                "guidance_scale": -0.1,
            },
            "guidance_scale",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Ambient.",
                "lyrics": "Instrumental",
                "guidance_scale": 20.1,
            },
            "guidance_scale",
        ),
        (
            {
                "app_id": APP_ID,
                "prompt": "Ambient.",
                "lyrics": "Instrumental",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_minimax_music_3_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        MinimaxMusic3Config.model_validate(payload)
