from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Lyria3Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/lyria3"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description=(
            "The text prompt describing the music you want to generate. Include genre, mood, "
            "instrumentation, tempo, and vocal style for best results. Lyria 3 supports vocals,"
            " lyrics, and multi-language generation."
        ),
    )
    negative_prompt: str = Field(
        default="",
        deprecated=True,
        description="Negative prompting is not supported by Lyria 3.",
    )
    image_url: str | None = Field(
        default=None,
        description=(
            "Optional image URL to use as inspiration for music generation. The model will "
            "create music that matches the mood and theme of the image."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
