"""Tests for the Nothing formatter obbject."""
from __future__ import annotations

import argparse

from flake8.formatting import default
from flake8.violation import Violation


def options(**kwargs):
    """Create an argparse.Namespace instance."""
    kwargs.setdefault("color", "auto")
    kwargs.setdefault("output_file", None)
    kwargs.setdefault("tee", False)
    return argparse.Namespace(**kwargs)


def test_format_returns_nothing():
    """Verify Nothing.format returns None."""
    formatter = default.Nothing(options())
    error = Violation("code", "file.py", 1, 1, "text", "1")

    assert formatter.format(error) is None


def test_show_source_returns_nothing():
    """Verify Nothing.show_source returns None."""
    formatter = default.Nothing(options())
    error = Violation("code", "file.py", 1, 1, "text", "1")

    assert formatter.show_source(error) is None
