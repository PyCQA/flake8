"""Tests for the flake8.exceptions module."""
import pickle

import entrypoints

from flake8 import exceptions
from flake8.plugins import manager as plugins_manager


class _ExceptionTest:
    def test_pickleable(self):
        """Test that the exception is round-trip pickleable."""
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            new_err = pickle.loads(pickle.dumps(self.err, protocol=proto))
            assert str(self.err) == str(new_err)
            orig_e = self.err.original_exception
            new_e = new_err.original_exception
            assert (type(orig_e), orig_e.args) == (type(new_e), new_e.args)


class TestFailedToLoadPlugin(_ExceptionTest):
    """Tests for the FailedToLoadPlugin exception."""

    err = exceptions.FailedToLoadPlugin(
        plugin=plugins_manager.Plugin(
            'plugin_name',
            entrypoints.EntryPoint('plugin_name', 'os.path', None),
        ),
        exception=ValueError('boom!'),
    )


class TestInvalidSyntax(_ExceptionTest):
    """Tests for the InvalidSyntax exception."""

    err = exceptions.InvalidSyntax(exception=ValueError('Unexpected token: $'))


class TestPluginRequestedUnknownParameters(_ExceptionTest):
    """Tests for the PluginRequestedUnknownParameters exception."""

    err = exceptions.PluginRequestedUnknownParameters(
        plugin={'plugin_name': 'plugin_name'},
        exception=ValueError('boom!'),
    )


class TestPluginExecutionFailed(_ExceptionTest):
    """Tests for the PluginExecutionFailed exception."""

    err = exceptions.PluginExecutionFailed(
        plugin={'plugin_name': 'plugin_name'},
        exception=ValueError('boom!'),
    )
