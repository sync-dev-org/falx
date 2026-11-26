from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.lyria3 import Lyria3Config


class Lyria35Config(Lyria3Config):
    app_id: Literal["google/lyria-3.5"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description=(
            "The text prompt describing the music you want to generate. Include genre, mood, "
            "instrumentation, tempo, vocals, and structure for best results. Lyria 3.5 supports"
            " full-length songs up to a few minutes — use timestamps or duration hints in your "
            "prompt to control song length, e.g. 'a 2-minute track' or section markers like "
            "'[0:00-0:30] Intro: ...' / '[0:30-1:00] Verse: ...'. Supports English, German, "
            "Spanish, French, Hindi, Japanese, Korean, and Portuguese."
        ),
    )
    negative_prompt: str = Field(
        default="",
        deprecated=True,
        description="Negative prompting is not supported by Lyria 3.5.",
    )
    image_url: str | None = Field(
        default=None,
        description=(
            "Optional image URL to use as visual inspiration for music generation. The model "
            "will create music that matches the mood and theme of the image."
        ),
    )
