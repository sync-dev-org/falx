from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from falx.models import BaseFalConfig


class KlingV4LongImageConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["kling/v4/long-image"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=166000,
        description="Text prompt for the long image. Reference images as @Image1, @Image2, ...",
    )
    skill: Literal["ecommerce", "webpage"] = Field(
        default="webpage",
        description=(
            "'ecommerce' designs a product detail page and requires 1-3 product images; "
            "'webpage' designs a website."
        ),
    )
    image_urls: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=3,
        description=(
            "Product reference images (1-3) for 'ecommerce', referenced as "
            "@Image1, @Image2, ... Not supported for 'webpage'."
        ),
    )
    style_image_url: str | None = Field(
        default=None,
        description=(
            "Optional 'webpage' style reference: the design follows its visual and layout style. "
            "Referenced as @StyleImage. Not supported for 'ecommerce'."
        ),
    )
    subject_image_url: str | None = Field(
        default=None,
        description=(
            "Optional 'webpage' subject reference: "
            "the design is built around the subject it shows. "
            "Referenced as @SubjectImage. Not supported for 'ecommerce'."
        ),
    )
    length: Literal["short", "medium", "long"] = Field(
        default="medium",
        description=(
            "Page length for 'ecommerce': short (~2-5 sections), medium (~6-10) "
            "or long (~11-18). Ignored for 'webpage'."
        ),
    )
    resolution: Literal["1K", "2K"] = Field(
        default="1K",
        description="Output resolution.",
    )
    sync_mode: bool = Field(
        default=False,
        description="If `True`, the media will be returned as a data URI.",
    )

    @model_validator(mode="after")
    def validate_skill_inputs(self) -> Self:
        if self.skill == "ecommerce":
            if not self.image_urls:
                raise ValueError("image_urls is required for ecommerce")
            if self.style_image_url is not None:
                raise ValueError("style_image_url is not supported for ecommerce")
            if self.subject_image_url is not None:
                raise ValueError("subject_image_url is not supported for ecommerce")
        elif self.image_urls is not None:
            raise ValueError("image_urls is not supported for webpage")
        return self
