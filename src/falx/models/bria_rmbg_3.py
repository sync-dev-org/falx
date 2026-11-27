from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class BriaRmbg3Config(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bria/rmbg-3"]
    image_url: str = Field(
        ...,
        description="Input image to remove the background from (file or URL).",
    )
    prompt: str | None = Field(
        default=None,
        description=(
            "Optional. Plain words for how to change the default cutout of the photo's "
            "obvious subject: add something ('the person with the mat and the plant'), "
            "drop something ('the woman at her desk without the lamp') or narrow it "
            "('only the chair'). Everything kept is the original pixels with a new "
            "alpha channel. Leave it empty for the plain cutout of the obvious subject."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description="If true, returns the image directly in the response (increases latency).",
    )
