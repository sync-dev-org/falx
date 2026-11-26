from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

KlingV4AspectRatio = Literal["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]
KlingV4ReferenceAspectRatio = Literal["auto", "16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]
KlingV4Resolution = Literal["720p", "1080p", "4k"]


class KlingV4Shot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="The prompt for this shot.",
    )
    duration: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Shot duration in seconds.",
    )


class KlingV4FlashElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frontal_image_url: str | None = Field(
        default=None,
        description="The frontal image of the element (main view).",
    )
    reference_image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=3,
        description="Additional views of the element from different angles (1-3).",
    )
    video_url: str | None = Field(
        default=None,
        description="A video of the element, used instead of images (3-8s).",
    )


class KlingV4Element(KlingV4FlashElement):
    voice_id: str | None = Field(
        default=None,
        description=(
            "Voice bound to this element. Create one with "
            "https://fal.ai/models/fal-ai/kling-video/create-voice"
        ),
    )


def validate_hdr(resolution: str, hdr: bool) -> None:
    if hdr and resolution == "720p":
        raise ValueError("hdr requires 1080p or 4k resolution")


def validate_prompt_input(prompt: str | None, multi_prompt: list[KlingV4Shot] | None) -> None:
    if prompt is None and multi_prompt is None:
        raise ValueError("prompt or multi_prompt is required")


def validate_multi_prompt_duration(multi_prompt: list[KlingV4Shot] | None) -> None:
    if multi_prompt is not None and not 3 <= sum(shot.duration for shot in multi_prompt) <= 30:
        raise ValueError("multi_prompt total duration must be between 3 and 30 seconds")


def validate_reference_limits(
    elements: list[KlingV4FlashElement] | None,
    image_urls: list[str] | None,
    *,
    start_image_url: str | None = None,
    middle_image_urls: list[str] | None = None,
    end_image_url: str | None = None,
    voice_ids: list[str] | None = None,
    keep_audio: bool = False,
) -> None:
    if sum(element.video_url is not None for element in elements or []) > 3:
        raise ValueError("at most 3 video elements are allowed")

    image_count = (
        len(image_urls or [])
        + (start_image_url is not None)
        + len(middle_image_urls or [])
        + (end_image_url is not None)
    )
    if image_count > 10:
        raise ValueError("at most 10 image references, including keyframes, are allowed")

    voice_count = len(voice_ids or []) + sum(
        isinstance(element, KlingV4Element) and element.voice_id is not None
        for element in elements or []
    )
    if voice_count > 3:
        raise ValueError("at most 3 voices, including voices bound to elements, are allowed")
    if keep_audio and voice_count:
        raise ValueError("keep_audio cannot be combined with voices")
