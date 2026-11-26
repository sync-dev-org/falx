from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    KlingO3ImageElementInput,
    KlingVideoO34kVideoToVideoEditConfig,
    config_class_for_app_id,
)

APP_ID = "fal-ai/kling-video/o3/4k/video-to-video/edit"


def test_kling_o3_4k_video_to_video_edit_accepts_schema_defaults() -> None:
    config = KlingVideoO34kVideoToVideoEditConfig(
        app_id=APP_ID,
        prompt="Change the environment to snow.",
        video_url="https://example.com/reference.mp4",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "enable_safety_checker": True,
        "prompt": "Change the environment to snow.",
        "video_url": "https://example.com/reference.mp4",
        "shot_type": "customize",
        "elements": None,
        "keep_audio": True,
        "image_urls": None,
    }


def test_kling_o3_4k_video_to_video_edit_accepts_all_fields() -> None:
    config = KlingVideoO34kVideoToVideoEditConfig(
        app_id=APP_ID,
        prompt="Replace the animal with @Element1 and use @Image1 styling.",
        video_url="https://example.com/reference.mov",
        elements=[
            KlingO3ImageElementInput(
                frontal_image_url="https://example.com/front.png",
                reference_image_urls=["https://example.com/side.png"],
            )
        ],
        keep_audio=False,
        image_urls=["https://example.com/style.png"],
    )

    assert config.keep_audio is False
    assert len(config.elements or []) == 1
    assert config.image_urls == ["https://example.com/style.png"]


def test_kling_o3_4k_video_to_video_edit_schema_preserves_4k_video_constraints() -> None:
    description = KlingVideoO34kVideoToVideoEditConfig.model_json_schema()["properties"][
        "video_url"
    ]["description"]

    assert description == (
        "Reference video URL. Only .mp4/.mov formats, 3-15s duration, "
        "720-3840px resolution, max 200MB."
    )


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"video_url": "https://example.com/reference.mp4"}, "prompt"),
        ({"prompt": "Edit the clip."}, "video_url"),
        (
            {
                "prompt": "x" * 2501,
                "video_url": "https://example.com/reference.mp4",
            },
            "prompt",
        ),
        (
            {
                "prompt": "Edit the clip.",
                "video_url": "https://example.com/reference.mp4",
                "shot_type": "intelligent",
            },
            "customize",
        ),
        (
            {
                "prompt": "Show @Element2.",
                "video_url": "https://example.com/reference.mp4",
                "elements": [{"frontal_image_url": "https://example.com/front.png"}],
            },
            "@Element2",
        ),
        (
            {
                "prompt": "Show @Image2.",
                "video_url": "https://example.com/reference.mp4",
                "image_urls": ["https://example.com/style.png"],
            },
            "@Image2",
        ),
        (
            {
                "prompt": "Edit the clip.",
                "video_url": "https://example.com/reference.mp4",
                "elements": [{"frontal_image_url": "https://example.com/front.png"}],
                "image_urls": [f"https://example.com/ref-{index}.png" for index in range(4)],
            },
            "Maximum 4 total",
        ),
        (
            {
                "prompt": "Edit the clip.",
                "video_url": "https://example.com/reference.mp4",
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_kling_o3_4k_video_to_video_edit_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        KlingVideoO34kVideoToVideoEditConfig.model_validate({"app_id": APP_ID, **parameters})


def test_kling_o3_4k_video_to_video_edit_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is KlingVideoO34kVideoToVideoEditConfig
    assert KlingVideoO34kVideoToVideoEditConfig.random_seed_field is None
