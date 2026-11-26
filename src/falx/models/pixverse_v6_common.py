from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field, field_validator

from falx.models import BaseFalConfig


class PixverseV6BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        description=(
            "Text prompt for the video generation. Limited to 2048 UTF-8 encoded bytes. "
            "Because the limit counts bytes rather than characters, emoji and non-Latin "
            "or accented characters (which use multiple bytes each) can push a visually "
            "short prompt over the cap."
        ),
    )
    resolution: Literal["360p", "540p", "720p", "1080p"] = Field(
        default="720p",
        description="The resolution of the generated video",
    )
    duration: int = Field(
        default=5,
        ge=1,
        le=15,
        description=(
            "The duration of the generated video in seconds. "
            "v6 supports values from 1 to 15 seconds"
        ),
    )
    negative_prompt: str = Field(
        default="",
        description=(
            "Negative prompt to be used for the generation. Limited to 2048 UTF-8 encoded "
            "bytes. Because the limit counts bytes rather than characters, emoji and "
            "non-Latin or accented characters (which use multiple bytes each) can push "
            "a visually short prompt over the cap."
        ),
    )
    style: Literal["anime", "3d_animation", "clay", "comic", "cyberpunk"] | None = Field(
        default=None,
        description="The style of the generated video",
    )
    seed: int | None = Field(
        default=None,
        description=(
            "The same seed and the same prompt given to the same version of the model "
            "will output the same video every time."
        ),
    )
    generate_audio_switch: bool = Field(
        default=False,
        description="Enable audio generation (BGM, SFX, dialogue)",
    )

    @field_validator("prompt", "negative_prompt")
    @classmethod
    def validate_prompt_byte_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 2048:
            raise ValueError("prompt must be at most 2048 UTF-8 encoded bytes")
        return value
