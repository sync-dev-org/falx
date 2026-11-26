from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.seedream_v5_flash_edit import SeedreamV5FlashEditConfig


class SeedreamV5ProUsEditConfig(SeedreamV5FlashEditConfig):
    app_id: Literal["bytedance/seedream/v5/pro/us/edit"]
    enhance_prompt_mode: Literal["standard", "fast"] = Field(
        default="standard",
        description=(
            "Prompt optimization mode. standard prioritizes image quality; fast reduces "
            "generation time."
        ),
    )
