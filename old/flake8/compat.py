# -*- coding: utf-8 -*-
"""Compatibility shims for Flake8."""
import os.path
import sys


def relpath(path, start='.'):
    """Wallpaper over the differences between 2.6 and newer versions."""
    if sys.version_info < (2, 7) and path.startswith(start):
        return path[len(start):]
    else:
        return os.path.relpath(path, start=start)
