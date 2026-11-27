from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from falx.models import BaseFalConfig


class BriaGuidedRemoveBackgroundConfig(BaseFalConfig):
    random_seed_field: ClassVar[str | None] = None

    app_id: Literal["bria/guided-remove-background"]
    image_url: str = Field(
        default="https://labs-assets.bria.ai/api-examples/guided-remove-background/yoga_studio_input.jpg",
        description=(
            "Source image as a public URL, a base64 data URI "
            "(data:image/png;base64,...) or raw base64-encoded image bytes."
        ),
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
    autocrop: bool = Field(
        default=False,
        description="Tighten the output canvas to the kept content.",
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "\n            If true, the function waits for the image to be generated "
            "and uploaded\n            before returning, so the image is returned "
            "directly (base64) instead of\n            via the CDN. Increases latency.\n "
            "       "
        ),
    )
