"""e2e smoke test session bootstrap.

Loads ``.env`` from the repository root so that ``FAL_KEY`` is available before
the ``skipif`` marker on ``test_smoke.py`` is evaluated.
"""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()
