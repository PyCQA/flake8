"""Integration tests for the checker submodule."""
import mock
import pytest

from flake8 import checker
from flake8.plugins import manager


EXPECTED_REPORT = (1, 1, 'T000 Expected Message')


class PluginClass(object):
    """Simple file plugin class yielding the expected report."""

    name = 'test'
    version = '1.0.0'

    def __init__(self, tree):
        """Dummy constructor to provide mandatory parameter."""
        pass

    def run(self):
        """Run class yielding one element containing the expected report."""
        yield EXPECTED_REPORT + (type(self), )


def plugin_func(func):
    """Decorator for file plugins which are implemented as functions."""
    func.name = 'test'
    func.version = '1.0.0'
    return func


@plugin_func
def plugin_func_gen(tree):
    """Simple file plugin function yielding the expected report."""
    yield EXPECTED_REPORT + (type(plugin_func_gen), )


@plugin_func
def plugin_func_list(tree):
    """Simple file plugin function returning a list of reports."""
    return [EXPECTED_REPORT + (type(plugin_func_list), )]


@pytest.mark.parametrize('plugin_target', [
    PluginClass,
    plugin_func_gen,
    plugin_func_list,
])
def test_handle_file_plugins(plugin_target):
    """Test the FileChecker class handling different file plugin types."""
    # Mock an entry point returning the plugin target
    entry_point = mock.Mock(spec=['require', 'resolve', 'load'])
    entry_point.name = plugin_target.name
    entry_point.resolve.return_value = plugin_target

    # Load the checker plugins using the entry point mock
    with mock.patch('pkg_resources.iter_entry_points',
                    return_value=[entry_point]):
        checks = manager.Checkers()

    # Prevent it from reading lines from stdin or somewhere else
    with mock.patch('flake8.processor.FileProcessor.read_lines',
                    return_value=['Line 1']):
        file_checker = checker.FileChecker('-', checks, mock.MagicMock())

    # Do not actually build an AST
    file_checker.processor.build_ast = lambda: True

    # Forward reports to this mock
    report = mock.Mock()
    file_checker.report = report
    file_checker.run_ast_checks()
    report.assert_called_once_with(error_code=None,
                                   line_number=EXPECTED_REPORT[0],
                                   column=EXPECTED_REPORT[1],
                                   text=EXPECTED_REPORT[2])
