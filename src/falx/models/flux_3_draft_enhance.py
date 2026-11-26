from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models import BaseFalConfig


class Flux3DraftEnhanceConfig(BaseFalConfig):
    app_id: Literal["blackforestlabs/flux-3/draft-enhance"]
    draft_cache_url: str = Field(
        ...,
        description="URL or data URI of the encrypted draft cache bundle to enhance.",
    )
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=4,
        description=(
            "The safety tolerance level for the generated video. "
            "0 is the strictest and 4 is the most permissive."
        ),
    )
