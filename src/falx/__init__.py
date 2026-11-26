"""falx — Python library and CLI wrapper for fal.ai queue APIs."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("falx")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
