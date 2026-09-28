"""Edgework NHL API Client - Version 0.11.0"""

from ._version import __version__

__all__ = ["Edgework", "__version__"]


def __getattr__(name: str):
    """Load the facade lazily so submodules do not create import cycles."""
    if name == "Edgework":
        from .edgework import Edgework

        return Edgework
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
