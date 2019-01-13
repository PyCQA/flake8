"""Shared fixtures between unit tests."""
import optparse

import pytest


def options_from(**kwargs):
    """Generate a Values instances with our kwargs."""
    kwargs.setdefault('hang_closing', True)
    kwargs.setdefault('max_line_length', 79)
    kwargs.setdefault('max_doc_length', None)
    kwargs.setdefault('verbose', False)
    kwargs.setdefault('stdin_display_name', 'stdin')
    return optparse.Values(kwargs)


@pytest.fixture
def default_options():
    """Fixture returning the default options of flake8."""
    return options_from()
