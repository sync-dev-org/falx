from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class HeygenVideoBaseConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    prompt: str = Field(..., min_length=1, max_length=32_000)
    duration: int = Field(default=5, ge=5, le=30)
    resolution: Literal["480p", "768p", "1080p", "2k"] = Field(default="768p")
    prompt_enhancement: Literal["turbo", "quality", "ultraquality", "disabled"] = Field(
        default="turbo",
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
    seed: int | None = Field(default=None, ge=0, le=4_294_967_295)
