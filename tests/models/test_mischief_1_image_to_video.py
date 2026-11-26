from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from falx.models import Mischief1ImageToVideoConfig

PAYLOAD = {
    "app_id": "tbc/mischief-1/image-to-video",
    "prompt": "A forest.",
    "image_url": "https://example.com/a.png",
}


def test_mischief_1_defaults() -> None:
    config = Mischief1ImageToVideoConfig.model_validate(PAYLOAD)
    assert config.model_dump() == {
        **PAYLOAD,
        "duration": 5,
        "resolution": "720p",
        "seed": None,
        "prompt_processing": "enhanced",
        "image_transform": "center_crop",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "x"),
        ("prompt", "x" * 2000),
        ("duration", 3),
        ("duration", 5),
        ("resolution", "480p"),
        ("resolution", "720p"),
        ("seed", 0),
        ("seed", 2147483647),
        ("prompt_processing", "original"),
        ("prompt_processing", "enhanced"),
        ("image_transform", "center_crop"),
        ("image_transform", "resize"),
    ],
)
def test_mischief_1_accepts_options(field: str, value: Any) -> None:
    config = Mischief1ImageToVideoConfig.model_validate({**PAYLOAD, field: value})
    assert getattr(config, field) == value


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", ""),
        ("prompt", "x" * 2001),
        ("duration", 2),
        ("duration", 4),
        ("duration", 6),
        ("resolution", "1080p"),
        ("seed", -1),
        ("seed", 2147483648),
        ("prompt_processing", "disabled"),
        ("image_transform", "crop"),
        ("unexpected", True),
    ],
)
def test_mischief_1_rejects_invalid_options(field: str, value: Any) -> None:
    with pytest.raises(ValidationError, match=field):
        Mischief1ImageToVideoConfig.model_validate({**PAYLOAD, field: value})


@pytest.mark.parametrize("field", ["prompt", "image_url"])
def test_mischief_1_requires_prompt_and_image(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        Mischief1ImageToVideoConfig.model_validate(
            {key: value for key, value in PAYLOAD.items() if key != field}
        )
