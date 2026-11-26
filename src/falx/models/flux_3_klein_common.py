from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig

Flux3KleinImageSizePreset = Literal[
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
]
FLUX3_KLEIN_IMAGE_SIZE_LIMITS = {
    "min_width": 256,
    "max_width": 4096,
    "min_height": 256,
    "max_height": 4096,
    "max_area": 16777216,
    "multiple_of": 16,
}


class Flux3KleinImageSize(BaseFalConfig):
    width: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="The width of the generated image.",
    )
    height: int = Field(
        default=512,
        gt=0,
        le=14142,
        description="The height of the generated image.",
    )


class Flux3KleinBox(BaseFalConfig):
    x_min: float = Field(
        ...,
        ge=0,
        le=1,
        description="Left edge as a fraction of the image width (0-1).",
    )
    y_min: float = Field(
        ...,
        ge=0,
        le=1,
        description="Top edge as a fraction of the image height (0-1).",
    )
    x_max: float = Field(
        ...,
        ge=0,
        le=1,
        description="Right edge as a fraction of the image width (0-1).",
    )
    y_max: float = Field(
        ...,
        ge=0,
        le=1,
        description="Bottom edge as a fraction of the image height (0-1).",
    )


class Flux3KleinBoundingBoxBase(BaseFalConfig):
    label: str | None = Field(
        default=None,
        max_length=64,
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
        description=(
            "Short name for the object in this box, e.g. `fox`. Write `<fox>` in the prompt "
            "to tie the box to those words; a box the prompt doesn't name is added to the scene. "
            "Defaults to `obj_<n>`."
        ),
    )
    description: str = Field(
        ...,
        max_length=500,
        description="What to draw in this box: the object and its look.",
    )


class Flux3KleinBoundingBox(Flux3KleinBoundingBoxBase):
    box: Flux3KleinBox = Field(
        ...,
        description="Where the object goes in the output image.",
    )


class Flux3KleinEditBoundingBox(Flux3KleinBoundingBoxBase):
    label: str | None = Field(
        default=None,
        max_length=64,
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
        description=(
            "Short name for the object in this box, e.g. `dragon`. Write `<dragon>` in the "
            "prompt to tie the box to those words; a box the prompt doesn't name is added to "
            "the scene. Defaults to `obj_<n>`."
        ),
    )
    box: Flux3KleinBox | None = Field(
        default=None,
        description=(
            "Where the object goes in the output image, as on text-to-image. "
            "Use instead of `source_box`/`target_box`."
        ),
    )
    source_image_index: int | None = Field(
        default=None,
        ge=0,
        description=(
            "0-based index into `image_urls` of the reference the object comes from. "
            "Leave unset for a new object."
        ),
    )
    source_box: Flux3KleinBox | None = Field(
        default=None,
        description="Where the object is in the reference image. Requires `source_image_index`.",
    )
    target_box: Flux3KleinBox | None = Field(
        default=None,
        description=(
            "Where the object goes in the output image. Leave unset to remove a referenced "
            "object; set both boxes to move or resize it."
        ),
    )

    @model_validator(mode="after")
    def validate_source_image_index(self) -> Self:
        if self.source_box is not None and self.source_image_index is None:
            raise ValueError("source_box requires source_image_index")
        return self


class Flux3KleinLoRAInput(BaseFalConfig):
    path: str = Field(
        ...,
        description=(
            "URL to a FLUX 3 Klein LoRA (.safetensors), e.g. from flux-3-image-klein-trainer."
        ),
    )
    scale: float = Field(
        default=1.0,
        ge=0,
        le=4,
        description="Scale factor for LoRA application (0.0 to 4.0).",
    )


class Flux3KleinCommon(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ...,
        description=(
            "The prompt to generate an image from. The model is trained on detailed captions: "
            "describe framing, subject, background and lighting."
        ),
    )
    enable_prompt_expansion: bool = Field(
        default=True,
        description=(
            "If set to true, the prompt is expanded into a detailed caption "
            "(grounded in the reference images when editing) before generation."
        ),
    )
    seed: int | None = Field(
        default=None,
        description=(
            "The same seed and the same prompt given to the same version of the model will "
            "output the same image every time."
        ),
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
        description="The number of images to generate.",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="If set to true, the safety checker will be enabled.",
    )
    output_format: Literal["jpeg", "png", "webp"] = Field(
        default="png",
        description="The format of the generated image.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data won't "
            "be available in the request history."
        ),
    )


class Flux3KleinLoraConfig(BaseFalConfig):
    loras: list[Flux3KleinLoRAInput] = Field(
        default_factory=list,
        max_length=3,
        description="LoRA weights to apply (maximum 3).",
    )


class Flux3KleinBaseLoraConfig(Flux3KleinLoraConfig):
    negative_prompt: str = Field(
        default="",
        description=(
            "The negative prompt to use. "
            "Use it to address details that you don't want in the image."
        ),
    )
    num_inference_steps: int = Field(
        default=50,
        ge=4,
        le=50,
        description="The number of inference steps to perform.",
    )
    guidance_scale: float = Field(
        default=3.5,
        ge=0,
        le=20,
        description="How closely the model should stick to your prompt (classifier-free guidance).",
    )
