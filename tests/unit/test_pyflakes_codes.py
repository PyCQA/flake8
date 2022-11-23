"""Tests of pyflakes monkey patches."""
from __future__ import annotations

import ast

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


def test_undefined_local_code():
    """In pyflakes 2.1.0 this code's string formatting was changed."""
    src = """\
import sys

def f():
    sys = sys
"""
    tree = ast.parse(src)
    checker = pyflakes_shim.FlakesChecker(tree, "t.py")
    message_texts = [s for _, _, s, _ in checker.run()]
    assert message_texts == [
        "F823 local variable 'sys' defined in enclosing scope on line 1 referenced before assignment",  # noqa: E501
        "F841 local variable 'sys' is assigned to but never used",
    ]
