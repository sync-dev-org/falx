from __future__ import annotations

from typing import Literal

from pydantic import Field

from falx.models.topaz_process_image_common import TopazProcessImageCommon


class TopazRestoreImageConfig(TopazProcessImageCommon):
    app_id: Literal["topaz/restore/image"]
    model: Literal["Recover 3", "Dust-Scratch V2"] = Field(
        default="Recover 3",
        description=(
            "Restoration. Recover 3 rebuilds natural detail; Dust-Scratch V2 cleans up film "
            "dust and scratches."
        ),
    )
