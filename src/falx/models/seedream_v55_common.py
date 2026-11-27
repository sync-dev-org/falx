from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from falx.models.seedream_v5_flash_common import SeedreamV5FlashCommon


class SeedreamV55Common(SeedreamV5FlashCommon):
    """Shared generation parameters for Seedream 5.5 text and edit endpoints."""

    output_format: Literal["jpeg", "png"] = Field(
        default="png",
        description="The file format of the generated image.",
    )
    background: Literal["auto", "opaque", "transparent"] = Field(
        default="auto",
        description=(
            "`auto` lets the model choose from the prompt and output format. "
            "`transparent` returns an RGBA image and requires `output_format=png`."
        ),
    )
    sync_mode: bool = Field(
        default=False,
        description=(
            "If `True`, the media will be returned as a data URI and the output data "
            "won't be available in the request history."
        ),
    )
    enable_safety_checker: bool = Field(
        default=True,
        description=(
            "If set to true, the safety checker will be enabled. Disabling it requires "
            "account authorization; unauthorized requests are always checked."
        ),
    )

    @model_validator(mode="after")
    def validate_transparent_output(self) -> SeedreamV55Common:
        if self.background == "transparent" and self.output_format != "png":
            raise ValueError("background='transparent' requires output_format='png'")
        return self
