from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from falx.models import BaseFalConfig
from falx.models.minimax_h3_image_to_video import MinimaxH3ImageToVideoConfig
from falx.models.minimax_h3_reference_to_video import MinimaxH3ReferenceToVideoConfig
from falx.models.minimax_h3_text_to_video import MinimaxH3TextToVideoConfig


class H3LoraInput(BaseFalConfig):
    """One LoRA adapter applied to H3 video generation."""

    path: str = Field(
        ...,
        description="URL or HuggingFace repo id (owner/repo) of the LoRA weights.",
    )
    scale: float = Field(
        default=1,
        ge=0,
        le=4,
        description="Strength of the LoRA (0.0 to 4.0).",
    )
    weight_name: str | None = Field(
        default=None,
        description=(
            "Name of the LoRA weight file. Only used when `path` is a HuggingFace "
            "repo and it holds more than one LoRA."
        ),
    )


H3Loras = Annotated[
    list[H3LoraInput],
    Field(
        min_length=1,
        max_length=3,
        description="List of LoRA adapters to apply to the transformer.",
    ),
]


class MinimaxH3TextToVideoLoraConfig(MinimaxH3TextToVideoConfig):
    app_id: Literal["minimax/h3/text-to-video/lora"]
    loras: H3Loras


class MinimaxH3ImageToVideoLoraConfig(MinimaxH3ImageToVideoConfig):
    app_id: Literal["minimax/h3/image-to-video/lora"]
    loras: H3Loras
    aspect_ratio: Literal["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="adaptive",
        description=(
            "The aspect ratio of the generated video. 'adaptive' follows the input "
            "image; a fixed ratio center-crops the keyframes to fit. Without "
            "keyframes, 'adaptive' generates 16:9."
        ),
    )


class MinimaxH3ReferenceToVideoLoraConfig(MinimaxH3ReferenceToVideoConfig):
    app_id: Literal["minimax/h3/reference-to-video/lora"]
    loras: H3Loras
