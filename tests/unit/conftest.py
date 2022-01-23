"""Shared fixtures between unit tests."""
import argparse

import pytest


def options_from(**kwargs):
    """Generate a Values instances with our kwargs."""
    kwargs.setdefault("hang_closing", True)
    kwargs.setdefault("max_line_length", 79)
    kwargs.setdefault("max_doc_length", None)
    kwargs.setdefault("indent_size", 4)
    kwargs.setdefault("verbose", 0)
    kwargs.setdefault("stdin_display_name", "stdin")
    kwargs.setdefault("disable_noqa", False)
    return argparse.Namespace(**kwargs)


@pytest.fixture
def default_options():
    """Fixture returning the default options of flake8."""
    return options_from()
