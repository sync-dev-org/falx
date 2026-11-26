from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from falx.models.minimax_h3_max_turbo_reference_to_video import (
    MinimaxH3MaxTurboReferenceToVideoConfig,
)


class MinimaxH3MaxReferenceToVideoConfig(MinimaxH3MaxTurboReferenceToVideoConfig):
    app_id: Literal["minimax/h3-max/reference-to-video"]
    image_url: Annotated[str, Field(min_length=1)] | None = Field(
        default=None,
        description=(
            "Optional URL of the image to use as the first frame. The video opens "
            "exactly on this image while the references keep the subjects consistent; "
            "the output canvas follows this image."
        ),
    )
    end_image_url: Annotated[str, Field(min_length=1)] | None = Field(
        default=None,
        description=(
            "Optional URL of the image to use as the last frame. "
            "The video ends exactly on this image."
        ),
    )
    middle_image_url: Annotated[str, Field(min_length=1)] | None = Field(
        default=None,
        description=(
            "Optional image to guide the video at middle_frame_time. Requires start "
            "and end images and native 480P or 768P resolution."
        ),
    )
    middle_frame_time: Annotated[float, Field(gt=0, lt=15)] | None = Field(
        default=None,
        description=(
            "Target time for the middle image, in seconds from the start. Rounded "
            "to the nearest frame at 24 fps; it must fall strictly between the first "
            "and last frames of the requested duration. Requires middle_image_url."
        ),
    )

    @model_validator(mode="after")
    def validate_middle_keyframe(self) -> Self:
        if self.middle_frame_time is not None and self.middle_image_url is None:
            raise ValueError("middle_frame_time requires middle_image_url")
        if self.middle_image_url is not None:
            if self.image_url is None or self.end_image_url is None:
                raise ValueError("middle_image_url requires image_url and end_image_url")
            if self.resolution not in {"480P", "768P"}:
                raise ValueError("middle_image_url requires native 480P or 768P resolution")
        return self
