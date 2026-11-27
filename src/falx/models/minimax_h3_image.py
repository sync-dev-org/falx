from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import Field

from falx.models.minimax_h3_image_common import MinimaxH3ImageCommon, MinimaxH3ImageLoraCommon


class MinimaxH3ImageTextToImageCommon(MinimaxH3ImageCommon):
    schema_example_parameters: ClassVar[dict[str, Any]] = {
        "image_size": {"width": 2048, "height": 2048},
    }

    enable_prompt_expansion: bool = Field(
        default=True,
        description=(
            "Rewrite the prompt with a language model into a detailed image "
            "description before generation. If expansion fails, the request fails "
            "instead of generating from the unexpanded prompt."
        ),
    )


class MinimaxH3ImageTextToImageConfig(MinimaxH3ImageTextToImageCommon, MinimaxH3ImageLoraCommon):
    app_id: Literal["minimax/h3-image/text-to-image"]


class MinimaxH3ImageHighspeedTextToImageConfig(MinimaxH3ImageTextToImageCommon):
    app_id: Literal["minimax/h3-image/highspeed/text-to-image"]
