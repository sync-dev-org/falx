from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_flash_text_to_image import SeedreamV5FlashTextToImageConfig


class SeedreamV5ProUsTextToImageConfig(SeedreamV5FlashTextToImageConfig):
    app_id: Literal["bytedance/seedream/v5/pro/us/text-to-image"]
    enhance_prompt_mode: Literal["standard", "fast"] = Field(
        default="standard",
        description=(
            "Prompt optimization mode. standard prioritizes image quality; fast reduces "
            "generation time."
        ),
    )
