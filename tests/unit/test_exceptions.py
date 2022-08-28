"""Tests for the flake8.exceptions module."""
from __future__ import annotations

import pickle

import pytest

from flake8 import exceptions


@pytest.mark.parametrize(
    "err",
    (
        exceptions.FailedToLoadPlugin(
            plugin_name="plugin_name",
            exception=ValueError("boom!"),
        ),
        exceptions.PluginRequestedUnknownParameters(
            plugin_name="plugin_name",
            exception=ValueError("boom!"),
        ),
        exceptions.PluginExecutionFailed(
            filename="filename.py",
            plugin_name="plugin_name",
            exception=ValueError("boom!"),
        ),
    ),
)
def test_pickleable(err):
    """Ensure that our exceptions can cross pickle boundaries."""
    for proto in range(pickle.HIGHEST_PROTOCOL + 1):
        new_err = pickle.loads(pickle.dumps(err, protocol=proto))
        assert str(err) == str(new_err)
        orig_e = err.original_exception
        new_e = new_err.original_exception
        assert (type(orig_e), orig_e.args) == (type(new_e), new_e.args)
