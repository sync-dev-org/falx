from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Sam31Label = Literal[0, 1]
Sam31ImageOutputFormat = Literal["jpeg", "png", "webp"]
Sam31VideoOutputType = Literal["X264 (.mp4)", "VP9 (.webm)"]


class Sam31PointPromptBase(BaseModel):
    """Point prompt without frame index (video endpoint)."""

    model_config = ConfigDict(extra="forbid")

    x: int | None = Field(
        default=None,
        description="X coordinate of the prompt.",
    )
    y: int | None = Field(
        default=None,
        description="Y coordinate of the prompt.",
    )
    label: Sam31Label | None = Field(
        default=None,
        description="1 for foreground, 0 for background.",
    )
    object_id: int | None = Field(
        default=None,
        description=(
            "Optional object identifier. Prompts sharing an object id refine the same object."
        ),
    )


class Sam31PointPrompt(Sam31PointPromptBase):
    """Point prompt with frame index (image / image-rle / video-rle)."""

    frame_index: int | None = Field(
        default=None,
        description="The frame index to interact with.",
    )


class Sam31BoxPromptBase(BaseModel):
    """Box prompt without frame index (video endpoint)."""

    model_config = ConfigDict(extra="forbid")

    x_min: int | None = Field(
        default=None,
        description="X min coordinate of the box.",
    )
    y_min: int | None = Field(
        default=None,
        description="Y min coordinate of the box.",
    )
    x_max: int | None = Field(
        default=None,
        description="X max coordinate of the box.",
    )
    y_max: int | None = Field(
        default=None,
        description="Y max coordinate of the box.",
    )
    object_id: int | None = Field(
        default=None,
        description=(
            "Optional object identifier. Boxes sharing an object id refine the same object."
        ),
    )


class Sam31BoxPrompt(Sam31BoxPromptBase):
    """Box prompt with frame index (image / image-rle / video-rle)."""

    frame_index: int | None = Field(
        default=None,
        description="The frame index to interact with.",
    )
