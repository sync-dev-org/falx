from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class MotionToCodeConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None
    schema_example_parameters: ClassVar[dict[str, Any]] = {
        "prompt": "A blob squashes, hops and lands; the word LOOP pops in letter by letter.",
    }

    prompt: str = Field(
        default="",
        max_length=4000,
        description=(
            "What to build, or what to change from the reference. Without a video, "
            "MiniMax H3 Max first animates it as a reference clip."
        ),
    )
    video_url: str | None = Field(
        default=None,
        description="Reference video to recreate, up to 15 s. Flat motion design works best.",
    )
    image_url: str | None = Field(
        default=None,
        description=(
            "Reference image: MiniMax H3 Max animates it, and the clip is rebuilt as code."
        ),
    )
    audio_url: str | None = Field(
        default=None,
        description=(
            "Soundtrack for the loop, up to 15 MB. With a prompt or an image, MiniMax H3 Max "
            "makes its clip to this sound. Without it, the reference's own sound is kept."
        ),
    )
    duration: float = Field(
        default=6,
        ge=1,
        le=15,
        description="Loop length in seconds. Ignored with a video, which sets it.",
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        default="16:9",
        description="Stage shape. Ignored with a video or an image, which set it.",
    )
    refine_rounds: int = Field(
        default=1,
        ge=0,
        le=1,
        description="Times the model compares its render with the reference and fixes it.",
    )
    enable_safety_checker: bool = True

    @model_validator(mode="after")
    def validate_reference_inputs(self) -> Self:
        if self.video_url and self.image_url:
            raise ValueError("video_url and image_url are mutually exclusive")
        if not (self.prompt or self.video_url or self.image_url):
            raise ValueError("At least one of prompt, video_url, or image_url is required")
        return self


class MotionToCodeGlslConfig(MotionToCodeConfig):
    app_id: Literal["fal-ai/motion-to-code/glsl"]


class MotionToCodeGsapConfig(MotionToCodeConfig):
    app_id: Literal["fal-ai/motion-to-code/gsap"]
