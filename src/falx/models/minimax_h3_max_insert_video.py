from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class MinimaxH3MaxInsertVideoConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = "seed"

    app_id: Literal["minimax/h3-max/insert-video"]
    video_url: str = Field(..., min_length=1)
    prompt: str | None = Field(default=None, min_length=1, max_length=50_000)
    reference_image_urls: list[str] = Field(default_factory=list, max_length=9)
    reference_video_urls: list[str] = Field(default_factory=list, max_length=3)
    start_time: float = Field(..., ge=1.625, le=60)
    resume_time: float = Field(..., gt=1.625, le=60)
    duration: float = Field(default=5, ge=5, le=13)
    resolution: Literal["480p", "768p"] = Field(default="768p")
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)
    enable_prompt_expansion: bool = Field(default=True)
    color_match: bool = Field(default=True)
