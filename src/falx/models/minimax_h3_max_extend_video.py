from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxExtendVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/extend-video"]
    video_url: str = Field(
        ...,
        min_length=1,
        description=(
            "URL of the video to extend. Must be 1.625 s to 60 s long, up to 50 MB, "
            "aspect ratio between 0.4 and 2.5."
        ),
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="What happens next. Describe the continuation, not the source.",
    )
    reference_audio_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "Optional audio references for the continuation (2–15 seconds each, "
            "15 seconds combined). The full extended video retains its original "
            "source soundtrack, and its ending still conditions the transition. "
            "These clips guide the newly generated audio instead of using that "
            "soundtrack as an audio reference. Assign each clip a role in the prompt, "
            "such as 'Audio 1 for the voice' and 'Audio 2 for background music'."
        ),
    )
    enable_prompt_expansion: bool = Field(
        default=True,
        description=(
            "Automatically enhance the prompt using the source video to help keep "
            "the continuation consistent. May increase processing time."
        ),
    )
    duration: float = Field(
        default=5,
        ge=0.71,
        le=15,
        description=(
            "Seconds of new footage to add. The continuation clip also includes "
            "1.625 seconds from the source's ending and may be longer because of "
            "frame rounding."
        ),
    )
    resolution: Literal["480P", "768P", "1080P", "2K"] = Field(
        default="768P",
        description="Output video resolution.",
    )
    aspect_ratio: Literal["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="auto",
        description=(
            "Output aspect ratio. 'auto' follows the source video. Other values "
            "crop the video to fit the selected ratio."
        ),
    )
    seed: int | None = Field(
        default=None,
        description="Seed for the continuation. Random when omitted.",
    )
    output: Literal["extended", "continuation"] = Field(
        default="extended",
        description=(
            "'extended' returns the source and new footage as one video. "
            "'continuation' returns a clip that starts with a 1.625-second repeat "
            "of the source's ending, then shows the new footage."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Moderate the source video and the prompt.",
    )
