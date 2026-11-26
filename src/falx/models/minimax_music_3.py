from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxMusic3Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/music-3"]
    prompt: str = Field(
        ...,
        description=(
            "Music description: style, mood, vocals, instrumentation and arrangement. "
            "For precise control use a Structured Caption with global metadata (genre, "
            "BPM, key, emotional progression), vocal details, and a section-by-section "
            "arrangement."
        ),
    )
    lyrics: str = Field(
        ...,
        description=(
            "The lyrics to sing. Structure tags such as [intro], [verse], [pre-chorus], "
            "[chorus], [post-chorus], [bridge], [instrumental], [solo] and [outro] must "
            "each be on their own line; text on the same line as a leading tag is "
            "dropped by the model's input contract."
        ),
    )
    duration: float = Field(
        default=60.0,
        ge=1,
        le=300,
        description=(
            "Upper bound on the generated audio length in seconds. The model may stop "
            "earlier; the actual duration is returned in the output."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Random seed for reproducibility. If not provided, a random seed will be used."
        ),
    )
    num_inference_steps: int = Field(
        default=30,
        ge=1,
        le=100,
        description=(
            "Number of flow-matching Euler steps per 8-second denoising chunk. More "
            "steps improve quality at the cost of speed."
        ),
    )
    guidance_scale: float = Field(
        default=1.7,
        ge=0,
        le=20,
        description="Classifier-free guidance scale of the flow-matching stage.",
    )
