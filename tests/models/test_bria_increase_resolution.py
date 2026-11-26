from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import (
    SUPPORTED_APP_IDS,
    BriaIncreaseResolutionConfig,
    config_class_for_app_id,
)

APP_ID = "bria/increase-resolution"


def test_bria_increase_resolution_accepts_schema_defaults() -> None:
    config = BriaIncreaseResolutionConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": "https://example.com/source.png",
        "desired_increase": 2,
        "output_type": "png",
        "preserve_alpha": True,
        "preserve_color": False,
        "sync_mode": False,
    }


def test_bria_increase_resolution_accepts_all_fields() -> None:
    config = BriaIncreaseResolutionConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.jpg",
        desired_increase=4,
        output_type="jpeg",
        preserve_alpha=False,
        preserve_color=True,
        sync_mode=True,
    )

    assert config.model_dump() == {
        "app_id": APP_ID,
        "image_url": "https://example.com/source.jpg",
        "desired_increase": 4,
        "output_type": "jpeg",
        "preserve_alpha": False,
        "preserve_color": True,
        "sync_mode": True,
    }


@pytest.mark.parametrize("desired_increase", [2, 4])
def test_bria_increase_resolution_accepts_increase_enum(desired_increase: int) -> None:
    config = BriaIncreaseResolutionConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
        desired_increase=desired_increase,
    )

    assert config.desired_increase == desired_increase


@pytest.mark.parametrize("output_type", ["png", "jpeg"])
def test_bria_increase_resolution_accepts_output_type_enum(output_type: str) -> None:
    config = BriaIncreaseResolutionConfig(
        app_id=APP_ID,
        image_url="https://example.com/source.png",
        output_type=output_type,
    )

    assert config.output_type == output_type


@pytest.mark.parametrize(
    ("parameters", "needle"),
    [
        ({}, "image_url"),
        (
            {"image_url": "https://example.com/source.png", "desired_increase": 3},
            "desired_increase",
        ),
        ({"image_url": "https://example.com/source.png", "output_type": "webp"}, "output_type"),
        ({"image_url": "https://example.com/source.png", "unexpected": True}, "unexpected"),
    ],
)
def test_bria_increase_resolution_rejects_invalid_payloads(
    parameters: dict[str, object],
    needle: str,
) -> None:
    with pytest.raises(ValidationError, match=needle):
        BriaIncreaseResolutionConfig.model_validate({"app_id": APP_ID, **parameters})


def test_bria_increase_resolution_is_registered() -> None:
    assert APP_ID in SUPPORTED_APP_IDS
    assert config_class_for_app_id(APP_ID) is BriaIncreaseResolutionConfig
    assert BriaIncreaseResolutionConfig.random_seed_field is None
