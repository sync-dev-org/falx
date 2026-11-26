from __future__ import annotations

import pytest
from pydantic import ValidationError

from falx.models import BaseFalConfig, config_class_for_app_id

APP_ID = "google/nano-banana-2.1/edit"


def parse(**parameters: object) -> BaseFalConfig:
    config_class = config_class_for_app_id(APP_ID)
    assert config_class is not None, f"{APP_ID} must be registered"
    return config_class(app_id=APP_ID, prompt="make the scene look like golden hour", **parameters)


def test_nano_banana_2_1_edit_accepts_image_context() -> None:
    urls = ["https://example.com/input.png", "./fixtures/local-input.png"]

    assert parse(image_urls=urls).image_urls == urls


@pytest.mark.parametrize("field_name", ["video_url", "pdf_url"])
def test_nano_banana_2_1_edit_accepts_non_image_context(field_name: str) -> None:
    url = "https://example.com/context"
    config = parse(**{field_name: url})

    assert not config.image_urls
    assert getattr(config, field_name) == url


def test_nano_banana_2_1_edit_accepts_empty_images_with_video_context() -> None:
    config = parse(image_urls=[], video_url="https://example.com/context.mp4")

    assert config.image_urls == []
    assert config.video_url == "https://example.com/context.mp4"


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"image_urls": []},
        {"video_url": None, "pdf_url": None},
        {"image_urls": [], "video_url": "", "pdf_url": ""},
    ],
)
def test_nano_banana_2_1_edit_requires_input_context(parameters: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="image_urls, video_url, or pdf_url"):
        parse(**parameters)


@pytest.mark.parametrize("images", [None, "https://example.com/input.png", [42]])
def test_nano_banana_2_1_edit_requires_an_image_url_array(images: object) -> None:
    with pytest.raises(ValidationError, match="image_urls"):
        parse(image_urls=images, pdf_url="https://example.com/context.pdf")


def test_nano_banana_2_1_edit_rejects_audio_context() -> None:
    with pytest.raises(ValidationError, match="audio_url"):
        parse(
            image_urls=["https://example.com/input.png"], audio_url="https://example.com/audio.mp3"
        )
