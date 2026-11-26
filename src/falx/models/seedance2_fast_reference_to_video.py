from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class Seedance2FastReferenceToVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bytedance/seedance-2.0/fast/reference-to-video"]
    prompt: str = Field(..., description="Text prompt used to generate the video.")
    image_urls: list[str] = Field(
        default_factory=list,
        max_length=9,
        description=(
            "Reference images that guide video generation. Refer to them in the "
            "prompt as @Image1, @Image2, and so on."
        ),
    )
    video_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "Reference videos that guide video generation. Refer to them in the "
            "prompt as @Video1, @Video2, and so on."
        ),
    )
    audio_urls: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=(
            "Reference audio files that guide video generation. Refer to them in the "
            "prompt as @Audio1, @Audio2, and so on; audio requires at least one image "
            "or video reference."
        ),
    )
    resolution: Literal["480p", "720p"] = Field(
        default="720p",
        description=(
            "Video resolution. 480p is faster and 720p balances speed and quality. "
            "Fast tier does not offer 1080p or 4k."
        ),
    )
    duration: Literal["auto", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"] = (
        Field(
            default="auto",
            description=(
                "Duration of the generated video in seconds. "
                "Allowed values: '4', '5', '6', '7', '8', '9', '10', '11', '12', "
                "'13', '14', '15' (string) or 'auto' (string) to let the model decide "
                "based on the prompt."
            ),
        )
    )
    aspect_ratio: Literal["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"] = Field(
        default="auto",
        description=(
            "Aspect ratio of the generated video. Use auto to let the model decide from the prompt."
        ),
    )
    generate_audio: bool = Field(
        default=True,
        description=(
            "Whether to generate synchronized audio, including sound effects, ambient "
            "sounds, and lip-synced speech."
        ),
    )
    bitrate_mode: Literal["standard", "high"] = Field(
        default="standard",
        description=(
            "Output bitrate mode. high requests a higher-quality, larger-file encode; "
            "standard uses the default bitrate."
        ),
    )
    codec: Literal["auto", "H264", "H265"] = Field(
        default="auto",
        description=(
            "'auto' uses the default video codec; US backend output is kept unchanged. "
            "'H264' and 'H265' select H.264 and H.265 respectively."
        ),
    )
    return_last_frame: bool = Field(
        default=False,
        description="If true, also return the last frame of the generated video as an image.",
    )
    end_user_id: str | None = Field(
        default=None,
        description="Unique user ID of the end user.",
    )

    @model_validator(mode="after")
    def validate_reference_file_constraints(self) -> Self:
        image_count = len(self.image_urls or [])
        video_count = len(self.video_urls or [])
        audio_count = len(self.audio_urls or [])

        if image_count + video_count + audio_count > 12:
            raise ValueError(
                "total files across image_urls, video_urls, and audio_urls must be <= 12"
            )
        if audio_count > 0 and image_count == 0 and video_count == 0:
            raise ValueError("audio_urls require image_urls or video_urls")
        return self
