from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.pixverse_v6_common import PixverseV6BaseConfig


class PixverseV6ExtendConfig(PixverseV6BaseConfig):
    app_id: Literal["fal-ai/pixverse/v6/extend"]
    video_url: str = Field(
        ...,
        description="URL of the input video to extend",
    )
    prompt: str = Field(
        ...,
        description=(
            "Prompt describing how to extend the video. Limited to 2048 UTF-8 encoded "
            "bytes. Because the limit counts bytes rather than characters, emoji and "
            "non-Latin or accented characters (which use multiple bytes each) can push "
            "a visually short prompt over the cap."
        ),
    )
    style: Literal["anime", "3d_animation", "clay", "comic", "cyberpunk"] | None = Field(
        default=None,
        description="The style of the extended video",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for generation",
    )
    generate_audio_switch: bool = Field(
        default=False,
        description="Enable audio generation (BGM, SFX, dialogue).",
    )
