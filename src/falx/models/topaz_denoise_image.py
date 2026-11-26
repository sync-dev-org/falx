from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.topaz_process_image_common import TopazProcessImageCommon


class TopazDenoiseImageConfig(TopazProcessImageCommon):
    app_id: Literal["topaz/denoise/image"]
    model: Literal["Normal", "Strong", "Extreme", "Denoise Max"] = Field(
        default="Normal",
        description=(
            "Denoise model. Normal is general-purpose; Strong and Extreme remove "
            "progressively more noise; Denoise Max is Topaz's highest-quality generative "
            "denoiser."
        ),
    )
