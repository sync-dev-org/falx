from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.topaz_process_image_common import TopazProcessImageCommon


class TopazSharpenImageConfig(TopazProcessImageCommon):
    app_id: Literal["topaz/sharpen/image"]
    model: Literal[
        "Standard",
        "Strong",
        "Lens Blur V2",
        "Motion Blur",
        "Natural",
        "Refocus",
        "Wildlife",
        "Portrait",
        "Auto Sharpen",
        "Super Focus V3",
        "Super Focus V2",
    ] = Field(
        default="Standard",
        description=(
            "Sharpen model tuned per blur type (defocus, motion, portrait, wildlife, …). "
            "Super Focus is Topaz's generative deblur for severely blurred images."
        ),
    )
