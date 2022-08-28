"""Tests for the FilenameOnly formatter object."""
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


def test_caches_filenames_already_printed():
    """Verify we cache filenames when we format them."""
    formatter = default.FilenameOnly(options())
    assert formatter.filenames_already_printed == set()

    formatter.format(Violation("code", "file.py", 1, 1, "text", "l"))
    assert formatter.filenames_already_printed == {"file.py"}


def test_only_returns_a_string_once_from_format():
    """Verify format ignores the second error with the same filename."""
    formatter = default.FilenameOnly(options())
    error = Violation("code", "file.py", 1, 1, "text", "1")

    assert formatter.format(error) == "file.py"
    assert formatter.format(error) is None


def test_show_source_returns_nothing():
    """Verify show_source returns nothing."""
    formatter = default.FilenameOnly(options())
    error = Violation("code", "file.py", 1, 1, "text", "1")

    assert formatter.show_source(error) is None
