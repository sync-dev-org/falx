from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class IdeogramVectorImageToVectorConfig(BaseFalConfig):
    app_id: Literal["ideogram/vector/image-to-vector"]
    image_url: str = Field(
        ..., description="The image to convert to SVG. JPEG, PNG or WebP, max 50MB."
    )
    mode: Literal["default", "simple"] = Field(
        default="default",
        description="`default` preserves finer details; `simple` uses fewer, simpler shapes.",
    )


class IdeogramVectorTextToVectorConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["ideogram/vector/text-to-vector"]
    prompt: str = Field(
        ..., min_length=1, max_length=9500, description="A text description of the SVG to generate."
    )
    quality: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Generation quality. `low` is fastest, `high` is highest quality.",
    )
    num_images: int = Field(default=1, ge=1, le=8, description="Number of SVGs to generate.")
    aspect_ratio: Literal[
        "auto",
        "1:1",
        "1:4",
        "1:3",
        "1:2",
        "9:16",
        "10:16",
        "2:3",
        "3:4",
        "4:5",
        "5:4",
        "4:3",
        "3:2",
        "16:10",
        "16:9",
        "2:1",
        "3:1",
        "4:1",
    ] = Field(default="auto", description="The aspect ratio of the generated SVG.")
    seed: int | None = Field(
        default=None, ge=0, le=2147483647, description="Seed for reproducible generation."
    )
    image_urls: list[str] | None = Field(
        default=None,
        max_length=5,
        description=(
            "Optional reference images (up to 5, max 10MB each). The first image is the primary "
            "source; the others are additional references."
        ),
    )
