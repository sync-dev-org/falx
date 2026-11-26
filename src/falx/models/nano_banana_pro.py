from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from falx.models.nano_banana_common import (
    GeminiDocumentPart,
    GeminiImagePart,
    GeminiMessage,
    GeminiSignaturePart,
    GeminiTextPart,
    NanoBananaCommon,
    NanoBananaExtendedAspectRatio,
)


class NanoBananaProCommon(NanoBananaCommon):
    """Shared parameters for nano-banana-pro generation and editing."""

    history: list[GeminiMessage] = Field(
        default_factory=list,
        description=(
            "Previous native user/model turns. Replay a returned conversation's messages "
            "unchanged, including thought signatures; the current prompt is appended as a new "
            "user turn."
        ),
    )
    context: list[
        Annotated[
            GeminiTextPart | GeminiImagePart | GeminiDocumentPart | GeminiSignaturePart,
            Field(discriminator="type"),
        ]
    ] = Field(
        default_factory=list,
        description=(
            "Ordered text, original images, PDF or UTF-8 text documents appended to the "
            "current prompt. Uses a native provider. Images count toward the total "
            "14-reference limit."
        ),
    )
    return_history: bool = Field(
        default=False,
        description=(
            "Return reusable native conversations with original image parts and provider "
            "thought signatures. Uses a native provider. Each generated conversation is "
            "independent; send its messages as history for the next turn."
        ),
    )
    thinking_level: Literal["high"] | None = Field(
        default=None,
        description=(
            "Thinking effort. Pro Image supports only high; omit to retain its provider "
            "default. An explicit level requests summaries unless include_thoughts overrides "
            "it. Thinking cannot be disabled."
        ),
    )
    include_thoughts: bool | None = Field(
        default=None,
        description=(
            "Whether to include thought summaries. Omit to preserve the existing behavior: an "
            "explicit thinking_level requests summaries. Set limit_generations=false to return "
            "summary text in description. This does not disable thinking or return "
            "intermediate thought images."
        ),
    )
    temperature: float | None = Field(
        default=None,
        ge=0,
        le=2,
        description=(
            "Sampling temperature. Omit to use the provider default of 1. Explicit values use "
            "a direct Google or Vertex API."
        ),
    )
    top_p: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Nucleus sampling probability. Omit to use the provider default of 0.95. Explicit "
            "values use a direct Google or Vertex API."
        ),
    )
    max_output_tokens: int | None = Field(
        default=None,
        ge=1,
        le=32768,
        description=(
            "Maximum output tokens for the generation. Omit to retain the provider default. "
            "Explicit values use a direct Google or Vertex API."
        ),
    )
    aspect_ratio: NanoBananaExtendedAspectRatio | None = Field(
        default="1:1",
        description="The aspect ratio of the generated image.",
    )
    system_prompt: str = Field(
        default="",
        max_length=50000,
        description=(
            "Optional system instruction that steers the model's persona and output style "
            "across the request. Leave blank to omit; when provided, it is sent as the system "
            "instruction to Gemini (or as a system message on OpenAI-compatible providers)."
        ),
    )
    resolution: Literal["1K", "2K", "4K"] = Field(
        default="1K",
        description="The resolution of the image to generate.",
    )
    enable_web_search: bool = Field(
        default=False,
        description=(
            "Enable web search for the image generation task. This will allow the model to use "
            "the latest information from the web to generate the image."
        ),
    )


class NanoBananaProConfig(NanoBananaProCommon):
    app_id: Literal["fal-ai/nano-banana-pro", "fal-ai/gemini-3-pro-image-preview"]
