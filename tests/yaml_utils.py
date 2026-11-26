from __future__ import annotations

from io import StringIO
from typing import Any

from ruamel.yaml import YAML, YAMLError

_SAFE_YAML = YAML(typ="safe")
_SAFE_YAML.default_flow_style = False


def safe_load(text: str) -> Any:
    return _SAFE_YAML.load(text)


def safe_dump(payload: Any, *, sort_keys: bool = False, allow_unicode: bool = True) -> str:
    if sort_keys:
        raise ValueError("safe_dump(sort_keys=True) is not supported")
    _SAFE_YAML.allow_unicode = allow_unicode
    buffer = StringIO()
    _SAFE_YAML.dump(payload, buffer)
    return buffer.getvalue()


__all__ = ["YAMLError", "safe_dump", "safe_load"]
