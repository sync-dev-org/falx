from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig
from falx.models.krea_3_common import Krea3Common, Krea3LoraConfig


class Krea3EditRegion(BaseFalConfig):
    image_idx: int = Field(
        ...,
        ge=0,
        description="Zero-based index into image_urls.",
    )
    x: float = Field(
        ...,
        ge=0,
        lt=1,
        description="Left edge as a fraction of image width.",
    )
    y: float = Field(
        ...,
        ge=0,
        lt=1,
        description="Top edge as a fraction of image height.",
    )
    width: float = Field(
        ...,
        gt=0,
        le=1,
        description="Width as a fraction of image width.",
    )
    height: float = Field(
        ...,
        gt=0,
        le=1,
        description="Height as a fraction of image height.",
    )
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        pattern=r"^[^\s@]+$",
        description="Refer to this region as @label. Defaults to its one-based position.",
    )
    note: str = Field(
        default="",
        max_length=5000,
        description="Edit instruction for this region; may reference other @labels.",
    )


class Krea3EditConfig(Krea3Common):
    schema_example_parameters: ClassVar[dict[str, Any]] = {"prompt": "<your prompt here>"}

    app_id: Literal["krea/v3/edit"]
    prompt: str = Field(
        default="",
        max_length=5000,
        description=(
            "Edit instruction. Refer to images as <image-1>, <image-2>, ... and regions as @label. "
            "May be omitted when a region has a note."
        ),
    )
    reasoning_level: Literal["medium", "high", "ultra"] = Field(
        default="medium",
        description=(
            "How much effort the prompt expander spends reasoning about the given editing task. "
            "Higher reasoning effort means slower generation time. `medium` is Krea's fast mode, "
            "`high` is Krea's high mode and `ultra` is Krea's ultra mode."
        ),
    )
    image_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=8,
        description="Reference images to edit or combine (1-8). Order sets the <image-N> tags.",
    )
    regions: list[Krea3EditRegion] | None = Field(
        default=None,
        max_length=24,
        description=(
            "Bounding boxes on reference images, with optional labels and editing notes. "
            "Requires high or ultra reasoning."
        ),
    )
    regional_edit: bool | None = Field(
        default=None,
        description=(
            "With high or ultra reasoning, true preserves pixels outside the edit regions on the "
            "chosen canvas; false disables automatic region cropping and preservation. Omit to "
            "retain automatic preservation. With image_size=auto, keeps the canvas dimensions; "
            "an explicit image_size preserves the resized input. Billing uses the generated "
            "render dimensions. Use PNG for lossless output."
        ),
    )

    @model_validator(mode="after")
    def validate_edit_instructions(self) -> Self:
        if self.regions and self.reasoning_level == "medium":
            raise ValueError("regions require reasoning_level high or ultra")
        if not self.prompt and not any(region.note for region in self.regions or []):
            raise ValueError("prompt or a region note is required")
        return self


class Krea3EditLoraConfig(Krea3EditConfig, Krea3LoraConfig):
    app_id: Literal["krea/v3/edit/lora"]
