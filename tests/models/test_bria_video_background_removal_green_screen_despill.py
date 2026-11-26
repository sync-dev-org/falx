from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    BriaVideoBackgroundRemovalGreenScreenDespillConfig,
    config_class_for_app_id,
)

APP_ID = "bria/video/background-removal/green-screen-despill"
OUTPUT_CODECS = [
    "mp4_h265",
    "mp4_h264",
    "webm_vp9",
    "mov_h265",
    "mov_proresks",
    "mkv_h265",
    "mkv_h264",
    "mkv_vp9",
    "gif",
]


def test_bria_green_screen_despill_accepts_schema_defaults() -> None:
    config = BriaVideoBackgroundRemovalGreenScreenDespillConfig(
        app_id=APP_ID,
        video_url="https://example.com/green-screen.webm",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "video_url": "https://example.com/green-screen.webm",
        "spill_suppression": 1.0,
        "preserve_audio": True,
        "output_container_and_codec": "webm_vp9",
    }


def test_bria_green_screen_despill_accepts_all_fields() -> None:
    config = BriaVideoBackgroundRemovalGreenScreenDespillConfig(
        app_id=APP_ID,
        video_url="https://example.com/green-screen.mov",
        spill_suppression=0.25,
        preserve_audio=False,
        output_container_and_codec="mov_proresks",
    )

    assert config.spill_suppression == 0.25
    assert config.preserve_audio is False
    assert config.output_container_and_codec == "mov_proresks"


@pytest.mark.parametrize("spill_suppression", [0.0, 1.0])
def test_bria_green_screen_despill_accepts_suppression_boundaries(
    spill_suppression: float,
) -> None:
    config = BriaVideoBackgroundRemovalGreenScreenDespillConfig(
        app_id=APP_ID,
        video_url="https://example.com/green-screen.webm",
        spill_suppression=spill_suppression,
    )

    assert config.spill_suppression == spill_suppression


@pytest.mark.parametrize("output_container_and_codec", OUTPUT_CODECS)
def test_bria_green_screen_despill_accepts_codec_enum(
    output_container_and_codec: str,
) -> None:
    config = BriaVideoBackgroundRemovalGreenScreenDespillConfig(
        app_id=APP_ID,
        video_url="https://example.com/green-screen.webm",
        output_container_and_codec=output_container_and_codec,
    )

    assert config.output_container_and_codec == output_container_and_codec


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "video_url"),
        (
            {"video_url": "https://example.com/video.mp4", "spill_suppression": -0.1},
            "spill_suppression",
        ),
        (
            {"video_url": "https://example.com/video.mp4", "spill_suppression": 1.1},
            "spill_suppression",
        ),
        (
            {
                "video_url": "https://example.com/video.mp4",
                "output_container_and_codec": "avi",
            },
            "output_container_and_codec",
        ),
        ({"video_url": "https://example.com/video.mp4", "unexpected": True}, "unexpected"),
    ],
)
def test_bria_green_screen_despill_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        BriaVideoBackgroundRemovalGreenScreenDespillConfig.model_validate(
            {"app_id": APP_ID, **parameters}
        )


def test_bria_green_screen_despill_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is BriaVideoBackgroundRemovalGreenScreenDespillConfig
    assert BriaVideoBackgroundRemovalGreenScreenDespillConfig.random_seed_field is None
