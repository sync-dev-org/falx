from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.pixverse_v6_common import PixverseV6BaseConfig


class PixverseV6MaxBaseConfig(PixverseV6BaseConfig):
    generate_multi_clip_switch: bool = Field(
        default=False,
        description="Enable multi-clip generation with dynamic camera changes",
    )
    thinking_type: Literal["enabled", "disabled", "auto"] | None = Field(
        default=None,
        description=(
            "Prompt optimization mode: 'enabled' to optimize, 'disabled' to turn off, "
            "'auto' for model decision"
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description="Authorized callers may set false to request relaxed screening.",
    )
