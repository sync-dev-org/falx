from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from falx.models.bria_fibo_2_common import BriaFibo2AspectRatio, BriaFibo2BaseConfig, BriaFibo2Vgl


class BriaFibo2GenerateConfig(BriaFibo2BaseConfig):
    app_id: Literal["bria/fibo-2/generate"]
    prompt: str | None = Field(
        default=None,
        description=(
            "What to generate, in free-form text. It is expanded into a VGL, which is "
            "returned. With 'vgl', the change to make to it."
        ),
    )
    style: Literal["Kodak Film", "Hard Flash", "Hazy Dreamy", "Rough Realism"] | None = Field(
        default=None,
        description=(
            "A style for the generated image. Requires 'prompt'; not with 'image_url', "
            "'vgl' or 'negative_prompt'."
        ),
    )
    image_url: str | None = Field(
        default=None,
        description=(
            "A reference image (inspire mode). With 'prompt', VGL uses it as a visual "
            "reference for the prompt's scene and generates a new image of that scene, "
            "not the image. Alone, the VGL describes the image itself, so the result "
            "is a close variation of it. Not with 'vgl'."
        ),
    )
    vgl: BriaFibo2Vgl | None = Field(
        default=None,
        description=(
            "A VGL (Visual Generation Language) document: the structured JSON "
            "description of the scene. Alone, the model renders it as-is. With "
            "'prompt', VGL changes it by the prompt (refine) and the result is "
            "rendered. Accepts what a previous request returned. Not with 'image_url' "
            "or 'style'."
        ),
    )
    aspect_ratio: BriaFibo2AspectRatio = Field(
        default="1:1",
        description=(
            "Aspect ratio of the image, at about one megapixel. Options: 1:1, 1:2, "
            "1:3, 1:4, 1:5, 2:1, 2:3, 3:1, 3:2, 3:4, 4:1, 4:3, 4:5, 5:1, 5:4, 9:16, "
            "9:21, 10:16, 16:9, 16:10, 21:9"
        ),
    )
    resolution: Literal["1K", "2K"] | None = Field(
        default=None,
        description=(
            "Size of the image. 1K (the default): about one megapixel, 1024x1024 at "
            "1:1 (1408x792 at 16:9). 2K: about four megapixels, the 1K image "
            "re-rendered at twice its width and height with finer detail, 2048x2048 at "
            "1:1 (2816x1584 at 16:9). The extra pass takes about three times as long "
            "as the image itself. 1MP and 4MP are accepted as the same two sizes."
        ),
    )

    @model_validator(mode="after")
    def validate_generation_modes(self) -> Self:
        if self.style is not None:
            if self.prompt is None:
                raise ValueError("style requires prompt")
            if self.image_url is not None or self.vgl is not None:
                raise ValueError("style cannot be combined with image_url or vgl")
        if self.image_url is not None and self.vgl is not None:
            raise ValueError("image_url cannot be combined with vgl")
        return self
