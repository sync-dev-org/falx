from __future__ import annotations

from typing import Literal

from falx.models.gemini_3_8_flash_tts import Gemini38FlashTtsConfig


class Gemini38FlashLiteTtsConfig(Gemini38FlashTtsConfig):
    app_id: Literal["google/gemini-3.8-flash-lite-tts"]
