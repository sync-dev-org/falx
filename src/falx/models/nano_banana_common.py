from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from falx.models import BaseFalConfig

NanoBananaAspectRatio = Literal[
    "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"
]
NanoBananaEditAspectRatio = Literal["auto", NanoBananaAspectRatio]
NanoBananaExtendedAspectRatio = Literal["auto", NanoBananaAspectRatio, "4:1", "1:4", "8:1", "1:8"]


class NanoBananaCommon(BaseFalConfig):
    """Shared image generation parameters for Nano Banana endpoints."""

    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=50000,
        description="The text prompt to generate an image from.",
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="The number of images to generate.",
    )
    seed: int | None = Field(
        default=None,
        description="The seed for the random number generator.",
    )
    aspect_ratio: NanoBananaAspectRatio = Field(
        default="1:1",
        description="The aspect ratio of the generated image.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="The format of the generated image.",
    )
    safety_tolerance: Literal["1", "2", "3", "4", "5", "6"] = Field(
        default="4",
        description=(
            "The safety tolerance level for content moderation. 1 is the most strict (blocks "
            "most content), 6 is the least strict."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data won't be "
            "available in the request history."
        ),
    )
    limit_generations: bool = Field(
        default=True,
        description=(
            "Experimental parameter to limit the number of generations from each round of "
            "prompting to 1. Set to `True` to to disregard any instructions in the prompt "
            "regarding the number of images to generate."
        ),
    )


class GeminiPartBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thought: bool | None = Field(
        default=None,
        description=("Provider thought marker, preserved when replaying a returned conversation."),
    )
    thought_signature: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Opaque provider-issued thought signature. Replay it unchanged on its original part."
        ),
    )


class GeminiTextPart(GeminiPartBase):
    type: Literal["text"] = Field(
        ...,
        description="The text part discriminator.",
    )
    text: str = Field(
        ...,
        description="Text at this position in the conversation.",
    )


class GeminiImagePart(GeminiPartBase):
    type: Literal["image"] = Field(
        ...,
        description="The image part discriminator.",
    )
    image_url: str = Field(
        ...,
        description=("Original image URL or data URI. Replayed without resizing or re-encoding."),
    )


class GeminiDocumentPart(GeminiPartBase):
    type: Literal["document"] = Field(
        ...,
        description="The document part discriminator.",
    )
    file_url: str = Field(
        ...,
        description="PDF or UTF-8 plain-text document URL or data URI (up to 15 MB).",
    )
    mime_type: Literal["application/pdf", "text/plain"] = Field(
        ...,
        description="The document's media type.",
    )


class GeminiSignaturePart(GeminiPartBase):
    thought_signature: str = Field(
        ...,
        min_length=1,
        description="Provider-issued signature-only part, replayed unchanged.",
    )
    type: Literal["signature"] = Field(
        ...,
        description="The signature part discriminator.",
    )


class GeminiVideoPart(GeminiPartBase):
    type: Literal["video"] = Field(
        ...,
        description="The video part discriminator.",
    )
    video_url: str = Field(
        ...,
        description=(
            "Video URL or data URI (up to 15 MB and 120 seconds), or a YouTube URL. Supported "
            "by Flash Image only."
        ),
    )


class GeminiAudioPart(GeminiPartBase):
    type: Literal["audio"] = Field(
        ...,
        description="The audio part discriminator.",
    )
    audio_url: str = Field(
        ...,
        description=(
            "Original audio URL or data URI from a previous Flash Image request (up to 15 MB)."
        ),
    )


class GeminiMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "model"] = Field(
        ...,
        description="Native Gemini conversation role.",
    )
    parts: list[
        Annotated[
            GeminiTextPart | GeminiImagePart | GeminiDocumentPart | GeminiSignaturePart,
            Field(discriminator="type"),
        ]
    ] = Field(
        ...,
        min_length=1,
        description="Ordered text, image, document, and signature parts.",
    )


class GeminiVideoMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "model"] = Field(
        ...,
        description="Native Gemini conversation role.",
    )
    parts: list[
        Annotated[
            GeminiTextPart
            | GeminiImagePart
            | GeminiDocumentPart
            | GeminiVideoPart
            | GeminiSignaturePart
            | GeminiAudioPart,
            Field(discriminator="type"),
        ]
    ] = Field(
        ...,
        min_length=1,
        description="Ordered text, image, document, video, audio, and signature parts.",
    )
