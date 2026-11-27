from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.krea_3_common import Krea3Common, Krea3LoraConfig


class Krea3TextToImageConfig(Krea3Common):
    app_id: Literal["krea/v3/text-to-image"]
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Description of the image to generate.",
    )
    reasoning_level: Literal["medium", "high"] = Field(
        default="medium",
        description=(
            "How much effort the prompt expander spends reasoning about the given prompt. "
            "Higher reasoning effort means slower generation time. `medium` is Krea's fast mode "
            "and `high` is Krea's high mode."
        ),
    )


class Krea3TextToImageLoraConfig(Krea3TextToImageConfig, Krea3LoraConfig):
    app_id: Literal["krea/v3/text-to-image/lora"]
