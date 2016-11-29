"""Tests of pyflakes monkey patches."""

import pyflakes

from flake8.plugins import pyflakes as pyflakes_shim


def test_all_pyflakes_messages_have_flake8_codes_assigned():
    """Verify all PyFlakes messages have error codes assigned."""
    messages = {
        name
        for name, obj in vars(pyflakes.messages).items()
        if name[0].isupper() and obj.message
    }
    assert messages == set(pyflakes_shim.FLAKE8_PYFLAKES_CODES)
