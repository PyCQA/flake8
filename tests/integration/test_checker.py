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
        file_checker = checker.FileChecker(
            '-',
            checks.to_dictionary(),
            mock.MagicMock()
        )

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


PLACEHOLDER_CODE = 'some_line = "of" * code'


@pytest.mark.parametrize('results, expected_order', [
    # No entries should be added
    ([], []),
    # Results are correctly ordered
    ([('A101', 1, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 1, 'placeholder error', PLACEHOLDER_CODE)], [0, 1]),
    # Reversed order of lines
    ([('A101', 2, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 1, 1, 'placeholder error', PLACEHOLDER_CODE)], [1, 0]),
    # Columns are not ordered correctly (when reports are ordered correctly)
    ([('A101', 1, 2, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 1, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 1, 'placeholder error', PLACEHOLDER_CODE)], [1, 0, 2]),
    ([('A101', 2, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 1, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 1, 2, 'placeholder error', PLACEHOLDER_CODE)], [1, 2, 0]),
    ([('A101', 1, 2, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 2, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 1, 'placeholder error', PLACEHOLDER_CODE)], [0, 2, 1]),
    ([('A101', 1, 3, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 2, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 3, 1, 'placeholder error', PLACEHOLDER_CODE)], [0, 1, 2]),
    ([('A101', 1, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 1, 3, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 2, 'placeholder error', PLACEHOLDER_CODE)], [0, 1, 2]),
    # Previously sort column and message (so reversed) (see bug 196)
    ([('A101', 1, 1, 'placeholder error', PLACEHOLDER_CODE),
      ('A101', 2, 1, 'charlie error', PLACEHOLDER_CODE)], [0, 1]),
])
def test_report_order(results, expected_order):
    """
    Test in which order the results will be reported.

    It gets a list of reports from the file checkers and verifies that the
    result will be ordered independent from the original report.
    """
    def count_side_effect(name, sorted_results):
        """Side effect for the result handler to tell all are reported."""
        return len(sorted_results)

    # To simplify the parameters (and prevent copy & pasting) reuse report
    # tuples to create the expected result lists from the indexes
    expected_results = [results[index] for index in expected_order]

    file_checker = mock.Mock(spec=['results', 'display_name'])
    file_checker.results = results
    file_checker.display_name = 'placeholder'

    style_guide = mock.Mock(spec=['options'])
    style_guide.processing_file = mock.MagicMock()

    # Create a placeholder manager without arguments or plugins
    # Just add one custom file checker which just provides the results
    manager = checker.Manager(style_guide, [], [])
    manager.checkers = [file_checker]

    # _handle_results is the first place which gets the sorted result
    # Should something non-private be mocked instead?
    handler = mock.Mock()
    handler.side_effect = count_side_effect
    manager._handle_results = handler

    assert manager.report() == (len(results), len(results))
    handler.assert_called_once_with('placeholder', expected_results)
