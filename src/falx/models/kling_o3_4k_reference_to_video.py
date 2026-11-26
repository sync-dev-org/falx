from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models.kling_o3_common import KlingO3ComboElementInput, validate_reference_indices
from falx.models.kling_o3_pro_reference_to_video import (
    KlingVideoO3ProReferenceToVideoConfig,
)


class KlingVideoO34kReferenceToVideoConfig(KlingVideoO3ProReferenceToVideoConfig):
    max_total_references_when_using_video: ClassVar[int] = 7
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["fal-ai/kling-video/o3/4k/reference-to-video"]
    elements: list[KlingO3ComboElementInput] | None = Field(
        default=None,
        description=(
            "Elements (characters/objects) to include. Reference in prompt as @Element1, @Element2."
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        description=(
            "Reference images for style/appearance. Reference in prompt as @Image1, "
            "@Image2, etc. Maximum 7 total (elements + reference images) is allowed."
        ),
    )

    @model_validator(mode="after")
    def validate_kling_o3_4k_r2v_constraints(self) -> Self:
        element_count = len(self.elements or [])
        image_count = len(self.image_urls or [])
        total_references = element_count + image_count

        if total_references > 7:
            raise ValueError("Maximum 7 total elements + image_urls is allowed")

        validate_reference_indices(
            self.prompt,
            self.multi_prompt,
            element_count=element_count,
            image_count=image_count,
        )
        return self
