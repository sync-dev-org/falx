from __future__ import annotations

from typing import Literal

from falx.models.nano_banana_common import NanoBananaCommon


class NanoBananaConfig(NanoBananaCommon):
    app_id: Literal["fal-ai/nano-banana", "fal-ai/gemini-25-flash-image"]
