from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig

Flux3ImageAspectRatio = Literal[
    "auto",
    "21:9",
    "2:1",
    "16:9",
    "3:2",
    "7:5",
    "4:3",
    "5:4",
    "1:1",
    "4:5",
    "3:4",
    "5:7",
    "2:3",
    "9:16",
    "1:2",
]


class Flux3ImageBaseConfig(BaseFalConfig):
    prompt: str = Field(
        ...,
        description="The prompt to generate an image from.",
    )
    aspect_ratio: Flux3ImageAspectRatio = Field(
        default="auto",
        description="Output aspect ratio. Auto uses the first reference image when editing.",
    )
    resolution: Literal["768sq", "1k", "1.5k", "2k", "4k"] = Field(
        default="1k",
        description="Output resolution tier. 4k can take several minutes.",
    )
    enable_prompt_expansion: bool = Field(
        default=False,
        description="Expand the prompt while preserving its intent and reference roles.",
    )
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=4,
        description="Safety tolerance, from 0 (strictest) to 4.",
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description="Return the image as a data URI instead of storing it in request history.",
    )
    version: Literal["latest"] = Field(
        default="latest",
        description="The model version.",
    )
