from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import ViduQ3ReferenceToVideoConfig


def test_vidu_q3_reference_to_video_accepts_schema_defaults() -> None:
    config = ViduQ3ReferenceToVideoConfig(
        app_id="fal-ai/vidu/q3/reference-to-video",
        prompt="A character walks across a beach while catching an apple.",
        reference_image_urls=[
            "https://example.com/ref-1.png",
            "https://example.com/ref-2.png",
        ],
    )

    assert config.model_dump() == {
        "app_id": "fal-ai/vidu/q3/reference-to-video",
        "prompt": "A character walks across a beach while catching an apple.",
        "reference_image_urls": [
            "https://example.com/ref-1.png",
            "https://example.com/ref-2.png",
        ],
        "duration": 5,
        "seed": None,
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "audio": True,
        "enable_safety_checker": True,
    }


@pytest.mark.parametrize("enable_safety_checker", [True, False, None])
def test_vidu_q3_reference_to_video_accepts_nullable_safety_checker(
    enable_safety_checker: bool | None,
) -> None:
    config = ViduQ3ReferenceToVideoConfig(
        app_id="fal-ai/vidu/q3/reference-to-video",
        prompt="Animate the references.",
        reference_image_urls=["https://example.com/ref.png"],
        enable_safety_checker=enable_safety_checker,
    )

    assert config.model_dump()["enable_safety_checker"] is enable_safety_checker


def test_vidu_q3_reference_to_video_accepts_all_fields() -> None:
    config = ViduQ3ReferenceToVideoConfig(
        app_id="fal-ai/vidu/q3/reference-to-video",
        prompt="Preserve the character identity across a studio camera move.",
        reference_image_urls=[
            "https://example.com/ref-1.png",
            "https://example.com/ref-2.png",
            "https://example.com/ref-3.png",
            "https://example.com/ref-4.png",
        ],
        duration=16,
        seed=777,
        aspect_ratio="1:1",
        resolution="540p",
        audio=False,
    )

    assert config.duration == 16
    assert config.seed == 777
    assert config.aspect_ratio == "1:1"
    assert config.resolution == "540p"
    assert config.audio is False


@pytest.mark.parametrize("duration", [1, 16])
def test_vidu_q3_reference_to_video_accepts_duration_boundaries(duration: int) -> None:
    config = ViduQ3ReferenceToVideoConfig(
        app_id="fal-ai/vidu/q3/reference-to-video",
        prompt="Animate the references.",
        reference_image_urls=["https://example.com/ref.png"],
        duration=duration,
    )

    assert config.duration == duration


@pytest.mark.parametrize("count", [1, 4])
def test_vidu_q3_reference_to_video_accepts_reference_image_count_boundaries(
    count: int,
) -> None:
    config = ViduQ3ReferenceToVideoConfig(
        app_id="fal-ai/vidu/q3/reference-to-video",
        prompt="Animate the references.",
        reference_image_urls=[
            f"https://example.com/ref-{index}.png" for index in range(1, count + 1)
        ],
    )

    assert len(config.reference_image_urls) == count


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (
            {
                "app_id": "fal-ai/vidu/q3/reference-to-video",
                "reference_image_urls": ["https://example.com/ref.png"],
            },
            "prompt",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/reference-to-video",
                "prompt": "Animate the references.",
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/reference-to-video",
                "prompt": "Animate the references.",
                "reference_image_urls": [],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/reference-to-video",
                "prompt": "Animate the references.",
                "reference_image_urls": [
                    "https://example.com/ref-1.png",
                    "https://example.com/ref-2.png",
                    "https://example.com/ref-3.png",
                    "https://example.com/ref-4.png",
                    "https://example.com/ref-5.png",
                ],
            },
            "reference_image_urls",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/reference-to-video",
                "prompt": "Animate the references.",
                "reference_image_urls": ["https://example.com/ref.png"],
                "duration": 0,
            },
            "duration",
        ),
        (
            {
                "app_id": "fal-ai/vidu/q3/reference-to-video",
                "prompt": "Animate the references.",
                "reference_image_urls": ["https://example.com/ref.png"],
                "aspect_ratio": "auto",
            },
            "aspect_ratio",
        ),
    ],
)
def test_vidu_q3_reference_to_video_rejects_invalid_payloads(
    payload: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        ViduQ3ReferenceToVideoConfig.model_validate(payload)
