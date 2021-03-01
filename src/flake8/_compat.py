"""Expose backports in a single place."""
import sys

if sys.version_info >= (3,):  # pragma: no cover (PY3+)
    from functools import lru_cache
else:  # pragma: no cover (<PY3)
    from functools32 import lru_cache

__all__ = ("lru_cache",)
