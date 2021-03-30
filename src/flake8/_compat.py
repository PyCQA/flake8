"""Expose backports in a single place."""
import sys
from functools import lru_cache

if sys.version_info >= (3, 8):  # pragma: no cover (PY38+)
    import importlib.metadata as importlib_metadata
else:  # pragma: no cover (<PY38)
    import importlib_metadata

__all__ = ("lru_cache", "importlib_metadata")
