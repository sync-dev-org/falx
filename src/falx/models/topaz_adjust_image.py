from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.topaz_process_image_common import TopazProcessImageCommon


class TopazAdjustImageConfig(TopazProcessImageCommon):
    app_id: Literal["topaz/adjust/image"]
    model: Literal["Adjust V2", "White Balance", "Colorize"] = Field(
        default="Adjust V2",
        description=(
            "Color & lighting correction. Adjust V2 fixes exposure/lighting; White Balance "
            "corrects color; Colorize adds color to B&W images."
        ),
    )
