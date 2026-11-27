from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.ideogram_v4 import IdeogramV4ImageSize, IdeogramV4ImageSizePreset


class IdeogramV46ContextWindowBox(BaseFalConfig):
    x_min: int = Field(..., ge=0, description="Left edge in source pixels (inclusive).")
    y_min: int = Field(..., ge=0, description="Top edge in source pixels (inclusive).")
    x_max: int = Field(..., ge=0, description="Right edge in source pixels (exclusive).")
    y_max: int = Field(..., ge=0, description="Bottom edge in source pixels (exclusive).")


class _IdeogramV46BaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(
        ..., min_length=1, max_length=10000, description="The generation or editing prompt."
    )
    image_size: IdeogramV4ImageSize | Literal["auto"] | IdeogramV4ImageSizePreset = Field(
        default="auto",
        description=(
            "Output size. auto lets the model pick a size of about 2K. Named presets use "
            "standard fal dimensions. Explicit dimensions must be at least 256 per side, "
            "multiples of 32, at most 4096 per side, with an aspect ratio within 1:6 and 6:1. "
            "Outputs larger than 2048x2048 in area are billed at the 4K price."
        ),
    )
    quality: Literal["very_low", "low", "medium", "high"] = Field(
        default="medium",
        description=(
            "Text-to-image quality. very_low renders at most 2K, so it rejects an explicit "
            "image_size larger than 2048x2048 in area."
        ),
    )
    background: Literal["transparent", "opaque"] | None = Field(
        default=None,
        description=(
            "transparent returns an image with an alpha channel; opaque forces a solid "
            "background. Leave unset for the model default."
        ),
    )
    num_images: int = Field(default=1, ge=1, le=8, description="Number of images to generate.")
    seed: int | None = Field(default=None, description="Random seed. Omit to choose automatically.")
    sync_mode: bool = Field(
        default=False, description="Return image data directly in the response."
    )
    enable_safety_checker: bool = Field(
        default=True, description="Authorized callers may set false to request relaxed screening."
    )


class IdeogramV46Config(_IdeogramV46BaseConfig):
    app_id: Literal["ideogram/v4.6"]
    enable_prompt_expansion: bool = Field(
        default=True, description="Enable partner prompt expansion."
    )


class IdeogramV46EditConfig(_IdeogramV46BaseConfig):
    app_id: Literal["ideogram/v4.6/edit"]
    image_url: str = Field(..., description="Primary source image to edit.")
    reference_image_urls: list[str] | None = Field(
        default=None,
        max_length=4,
        description=(
            "Up to four references plus the primary source, or three references plus the "
            "primary source and mask."
        ),
    )
    mask_url: str | None = Field(
        default=None,
        description=(
            "Mask matching the source dimensions. Black edits, white preserves. Must contain "
            "both regions after rounding."
        ),
    )
    edit_precision: Literal["regular", "high"] = Field(
        default="regular",
        description=(
            "regular uses Generate; high uses Precise Edit with unchanged-pixel restoration. "
            "Both always prepare structured edit instructions."
        ),
    )
    context_window: Literal["none", "auto"] = Field(
        default="none",
        description=(
            "Region to edit with high edit_precision. none edits the whole image, downscaled "
            "to at most 4194304 pixels. auto requires mask_url and fits the region around the "
            "mask; an oversized mask falls back to whole-image editing. Set context_window_box "
            "instead to pick the region yourself. Localized edits preserve the original image "
            "resolution and every pixel outside the region."
        ),
    )
    context_window_box: IdeogramV46ContextWindowBox | None = Field(
        default=None,
        description=(
            "Explicit region to edit with high edit_precision, in source pixels with exclusive "
            "x_max/y_max. Must lie inside the image, measure at least 256 pixels per side, "
            "cover at most 4194304 pixels, and have an aspect ratio within 1:6 and 6:1. A mask "
            "may select only pixels inside it. Cannot be combined with context_window auto. "
            "Leave unset to edit the whole image."
        ),
    )
    quality: Literal["very_low", "low", "medium", "high"] = Field(
        default="medium", description="Quality tier for either edit precision. Defaults to medium."
    )
    image_size: IdeogramV4ImageSize | Literal["auto"] | IdeogramV4ImageSizePreset = Field(
        default="auto",
        description=(
            "auto preserves source geometry. Only unmasked regular edits accept named presets "
            "or custom sizes: dimensions >=256, multiples of 32, at most 4096 per side, ratio "
            "<=6:1. very_low quality rejects a custom size larger than 2048x2048 in area. Named "
            "presets use standard fal dimensions. Outputs larger than 2048x2048 in area are "
            "billed at the 4K price."
        ),
    )
    background: Literal["transparent", "opaque"] | None = Field(
        default=None,
        description=(
            "Regular edits only. transparent returns an image with an alpha channel; opaque "
            "forces a solid background. Leave unset for the model default."
        ),
    )

    @model_validator(mode="after")
    def validate_edit_options(self) -> IdeogramV46EditConfig:
        if self.mask_url is not None and len(self.reference_image_urls or []) > 3:
            raise ValueError("reference_image_urls allows at most three references with mask_url")
        if self.context_window == "auto":
            if self.mask_url is None:
                raise ValueError("context_window auto requires mask_url")
            if self.context_window_box is not None:
                raise ValueError("context_window_box cannot be combined with context_window auto")
        if self.image_size != "auto" and (
            self.mask_url is not None or self.edit_precision != "regular"
        ):
            raise ValueError("image_size must be auto except for unmasked regular edits")
        if self.background is not None and self.edit_precision != "regular":
            raise ValueError("background is supported only for regular edits")
        return self
