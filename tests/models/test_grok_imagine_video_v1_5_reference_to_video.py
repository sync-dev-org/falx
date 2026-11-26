from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    GrokImagineVideoV15ReferenceToVideoConfig,
    config_class_for_app_id,
)

APP_ID = "xai/grok-imagine-video/v1.5/reference-to-video"
ASPECT_RATIOS = ["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "21:9", "5:2"]


def test_grok_imagine_video_v1_5_reference_to_video_accepts_schema_defaults() -> None:
    config = GrokImagineVideoV15ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="The person from <IMAGE_0> walks through a rainy street.",
        reference_image_urls=["https://example.com/person.png"],
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "prompt": "The person from <IMAGE_0> walks through a rainy street.",
        "reference_image_urls": ["https://example.com/person.png"],
        "duration": 8,
        "resolution": "480p",
        "aspect_ratio": "16:9",
        "generate_audio": None,
        "enable_safety_checker": True,
    }


def test_grok_imagine_video_v1_5_reference_to_video_accepts_all_fields() -> None:
    config = GrokImagineVideoV15ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Combine <IMAGE_0> and <IMAGE_6> in one scene.",
        reference_image_urls=[f"https://example.com/ref-{index}.png" for index in range(7)],
        duration=15,
        resolution="720p",
        aspect_ratio="9:16",
        generate_audio=False,
        enable_safety_checker=False,
    )

    assert len(config.reference_image_urls) == 7
    assert config.duration == 15
    assert config.resolution == "720p"
    assert config.aspect_ratio == "9:16"
    assert config.generate_audio is False
    assert config.enable_safety_checker is False


@pytest.mark.parametrize("generate_audio", [None, False, True])
def test_grok_imagine_video_v1_5_reference_to_video_accepts_optional_audio(
    generate_audio: bool | None,
) -> None:
    config = GrokImagineVideoV15ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Animate <IMAGE_0>.",
        reference_image_urls=["https://example.com/source.png"],
        generate_audio=generate_audio,
    )

    assert config.generate_audio is generate_audio
    payload = config.model_dump(exclude={"app_id"}, exclude_none=True)
    if generate_audio is None:
        assert "generate_audio" not in payload
    else:
        assert payload["generate_audio"] is generate_audio


@pytest.mark.parametrize("aspect_ratio", ASPECT_RATIOS)
@pytest.mark.parametrize("resolution", ["480p", "720p"])
@pytest.mark.parametrize("duration", [1, 15])
def test_grok_imagine_video_v1_5_reference_to_video_accepts_enums_and_boundaries(
    aspect_ratio: str,
    resolution: str,
    duration: int,
) -> None:
    config = GrokImagineVideoV15ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Animate <IMAGE_0>.",
        reference_image_urls=["https://example.com/source.png"],
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        duration=duration,
    )

    assert config.aspect_ratio == aspect_ratio
    assert config.resolution == resolution
    assert config.duration == duration


@pytest.mark.parametrize("image_count", [1, 7])
def test_grok_imagine_video_v1_5_reference_to_video_accepts_reference_boundaries(
    image_count: int,
) -> None:
    config = GrokImagineVideoV15ReferenceToVideoConfig(
        app_id=APP_ID,
        prompt="Animate the references.",
        reference_image_urls=[
            f"https://example.com/ref-{index}.png" for index in range(image_count)
        ],
    )

    assert len(config.reference_image_urls) == image_count


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({"reference_image_urls": ["https://example.com/source.png"]}, "prompt"),
        ({"prompt": "Animate the reference."}, "reference_image_urls"),
        ({"prompt": "Animate the reference.", "reference_image_urls": []}, "reference_image_urls"),
        (
            {
                "prompt": "Animate the reference.",
                "reference_image_urls": [str(index) for index in range(8)],
            },
            "reference_image_urls",
        ),
        (
            {
                "prompt": "x" * 4097,
                "reference_image_urls": ["https://example.com/source.png"],
            },
            "prompt",
        ),
        (
            {
                "prompt": "Animate the reference.",
                "reference_image_urls": ["https://example.com/source.png"],
                "aspect_ratio": "auto",
            },
            "aspect_ratio",
        ),
        (
            {
                "prompt": "Animate the reference.",
                "reference_image_urls": ["https://example.com/source.png"],
                "resolution": "1080p",
            },
            "resolution",
        ),
        (
            {
                "prompt": "Animate the reference.",
                "reference_image_urls": ["https://example.com/source.png"],
                "duration": 16,
            },
            "duration",
        ),
        (
            {
                "prompt": "Animate the reference.",
                "reference_image_urls": ["https://example.com/source.png"],
                "unexpected": True,
            },
            "unexpected",
        ),
    ],
)
def test_grok_imagine_video_v1_5_reference_to_video_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        GrokImagineVideoV15ReferenceToVideoConfig.model_validate({"app_id": APP_ID, **parameters})


def test_grok_imagine_video_v1_5_reference_to_video_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is GrokImagineVideoV15ReferenceToVideoConfig
    assert GrokImagineVideoV15ReferenceToVideoConfig.random_seed_field is None
