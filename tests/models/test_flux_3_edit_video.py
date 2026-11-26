from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    Flux3EditVideoConfig,
    config_class_for_app_id,
)

APP_ID = "blackforestlabs/flux-3/edit-video"


def test_flux_3_edit_video_accepts_schema_defaults() -> None:
    config = Flux3EditVideoConfig(
        app_id=APP_ID,
        prompt="Make it snow heavily.",
        video_url="https://example.com/source.mp4",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "Make it snow heavily.",
        "video_url": "https://example.com/source.mp4",
        "safety_tolerance": 2,
    }


def test_flux_3_edit_video_accepts_all_fields() -> None:
    config = Flux3EditVideoConfig(
        app_id=APP_ID,
        prompt="Give the scene a cold winter palette.",
        video_url="https://example.com/source.mp4",
        safety_tolerance=4,
    )

    assert config.safety_tolerance == 4


@pytest.mark.parametrize("safety_tolerance", [0, 4])
def test_flux_3_edit_video_accepts_safety_tolerance_boundaries(
    safety_tolerance: int,
) -> None:
    config = Flux3EditVideoConfig(
        app_id=APP_ID,
        prompt="Re-render the clip.",
        video_url="https://example.com/source.mp4",
        safety_tolerance=safety_tolerance,
    )

    assert config.safety_tolerance == safety_tolerance


def test_flux_3_edit_video_schema_preserves_route_specific_constraints() -> None:
    schema = Flux3EditVideoConfig.model_json_schema()

    assert schema["properties"]["prompt"]["maxLength"] == 4096
    assert schema["properties"]["video_url"]["description"] == (
        "URL of the input video. MP4, under 50 MB and under 15 seconds."
    )


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"video_url": "https://example.com/source.mp4"}, "prompt"),
        ({"prompt": "Re-render the clip."}, "video_url"),
        (
            {
                "prompt": "x" * 4097,
                "video_url": "https://example.com/source.mp4",
            },
            "prompt",
        ),
        (
            {
                "prompt": "Re-render the clip.",
                "video_url": "https://example.com/source.mp4",
                "safety_tolerance": -1,
            },
            "safety_tolerance",
        ),
        (
            {
                "prompt": "Re-render the clip.",
                "video_url": "https://example.com/source.mp4",
                "safety_tolerance": 5,
            },
            "safety_tolerance",
        ),
        (
            {
                "prompt": "Re-render the clip.",
                "video_url": "https://example.com/source.mp4",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_flux_3_edit_video_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        Flux3EditVideoConfig.model_validate({"app_id": APP_ID, **parameters})


def test_flux_3_edit_video_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is Flux3EditVideoConfig
    assert Flux3EditVideoConfig.random_seed_field is None
