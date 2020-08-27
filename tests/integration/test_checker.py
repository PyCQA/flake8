"""Integration tests for the checker submodule."""
import mock
import pytest

from flake8 import checker
from flake8._compat import importlib_metadata
from flake8.plugins import manager
from flake8.processor import FileProcessor

PHYSICAL_LINE = "# Physical line content"

EXPECTED_REPORT = (1, 1, 'T000 Expected Message')
EXPECTED_REPORT_PHYSICAL_LINE = (1, 'T000 Expected Message')
EXPECTED_RESULT_PHYSICAL_LINE = (
    'T000',
    0,
    1,
    'Expected Message',
    None,
)


class PluginClass(object):
    """Simple file plugin class yielding the expected report."""

    name = 'test'
    version = '1.0.0'

    def __init__(self, tree):
        """Construct a dummy object to provide mandatory parameter."""
        pass

    def run(self):
        """Run class yielding one element containing the expected report."""
        yield EXPECTED_REPORT + (type(self), )


def plugin_func(func):
    """Decorate file plugins which are implemented as functions."""
    func.name = 'test'
    func.version = '1.0.0'
    return func


@plugin_func
def plugin_func_gen(tree):
    """Yield the expected report."""
    yield EXPECTED_REPORT + (type(plugin_func_gen), )


@plugin_func
def plugin_func_list(tree):
    """Return a list of expected reports."""
    return [EXPECTED_REPORT + (type(plugin_func_list), )]


@plugin_func
def plugin_func_physical_ret(physical_line):
    """Expect report from a physical_line. Single return."""
    return EXPECTED_REPORT_PHYSICAL_LINE


@plugin_func
def plugin_func_physical_none(physical_line):
    """Expect report from a physical_line. No results."""
    return None


@plugin_func
def plugin_func_physical_list_single(physical_line):
    """Expect report from a physical_line. List of single result."""
    return [EXPECTED_REPORT_PHYSICAL_LINE]


@plugin_func
def plugin_func_physical_list_multiple(physical_line):
    """Expect report from a physical_line. List of multiple results."""
    return [EXPECTED_REPORT_PHYSICAL_LINE] * 2


@plugin_func
def plugin_func_physical_gen_single(physical_line):
    """Expect report from a physical_line. Generator of single result."""
    yield EXPECTED_REPORT_PHYSICAL_LINE


@plugin_func
def plugin_func_physical_gen_multiple(physical_line):
    """Expect report from a physical_line. Generator of multiple results."""
    for _ in range(3):
        yield EXPECTED_REPORT_PHYSICAL_LINE


def mock_file_checker_with_plugin(plugin_target):
    """Get a mock FileChecker class with plugin_target registered.

    Useful as a starting point for mocking reports/results.
    """
    # Mock an entry point returning the plugin target
    entry_point = mock.Mock(spec=['load'])
    entry_point.name = plugin_target.name
    entry_point.load.return_value = plugin_target
    entry_point.value = 'mocked:value'

    # Load the checker plugins using the entry point mock
    with mock.patch.object(
            importlib_metadata,
            'entry_points',
            return_value={'flake8.extension': [entry_point]},
    ):
        checks = manager.Checkers()

    # Prevent it from reading lines from stdin or somewhere else
    with mock.patch('flake8.processor.FileProcessor.read_lines',
                    return_value=['Line 1']):
        file_checker = checker.FileChecker(
            '-',
            checks.to_dictionary(),
            mock.MagicMock()
        )
    return file_checker


@pytest.mark.parametrize('plugin_target', [
    PluginClass,
    plugin_func_gen,
    plugin_func_list,
])
def test_handle_file_plugins(plugin_target):
    """Test the FileChecker class handling different file plugin types."""
    file_checker = mock_file_checker_with_plugin(plugin_target)

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


@pytest.mark.parametrize('plugin_target,len_results', [
    (plugin_func_physical_ret, 1),
    (plugin_func_physical_none, 0),
    (plugin_func_physical_list_single, 1),
    (plugin_func_physical_list_multiple, 2),
    (plugin_func_physical_gen_single, 1),
    (plugin_func_physical_gen_multiple, 3),
])
def test_line_check_results(plugin_target, len_results):
    """Test the FileChecker class handling results from line checks."""
    file_checker = mock_file_checker_with_plugin(plugin_target)

    # Results will be stored in an internal array
    file_checker.run_physical_checks(PHYSICAL_LINE)
    expected = [EXPECTED_RESULT_PHYSICAL_LINE] * len_results
    assert file_checker.results == expected


def test_logical_line_offset_out_of_bounds():
    """Ensure that logical line offsets that are out of bounds do not crash."""

    @plugin_func
    def _logical_line_out_of_bounds(logical_line):
        yield 10000, 'L100 test'

    file_checker = mock_file_checker_with_plugin(_logical_line_out_of_bounds)

    logical_ret = (
        '',
        'print("xxxxxxxxxxx")',
        [(0, (1, 0)), (5, (1, 5)), (6, (1, 6)), (19, (1, 19)), (20, (1, 20))],
    )
    with mock.patch.object(
        FileProcessor, 'build_logical_line', return_value=logical_ret,
    ):
        file_checker.run_logical_checks()
        assert file_checker.results == [('L100', 0, 0, 'test', None)]


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

    style_guide = mock.MagicMock(spec=['options', 'processing_file'])

    # Create a placeholder manager without arguments or plugins
    # Just add one custom file checker which just provides the results
    manager = checker.Manager(style_guide, [], [])
    manager.checkers = manager._all_checkers = [file_checker]

    # _handle_results is the first place which gets the sorted result
    # Should something non-private be mocked instead?
    handler = mock.Mock(side_effect=count_side_effect)
    with mock.patch.object(manager, '_handle_results', handler):
        assert manager.report() == (len(results), len(results))
        handler.assert_called_once_with('placeholder', expected_results)


def test_acquire_when_multiprocessing_pool_can_initialize():
    """Verify successful importing of hardware semaphore support.

    Mock the behaviour of a platform that has a hardware sem_open
    implementation, and then attempt to initialize a multiprocessing
    Pool object.

    This simulates the behaviour on most common platforms.
    """
    with mock.patch("multiprocessing.Pool") as pool:
        result = checker._try_initialize_processpool(2)

    pool.assert_called_once_with(2, checker._pool_init)
    assert result is pool.return_value


def test_acquire_when_multiprocessing_pool_can_not_initialize():
    """Verify unsuccessful importing of hardware semaphore support.

    Mock the behaviour of a platform that has not got a hardware sem_open
    implementation, and then attempt to initialize a multiprocessing
    Pool object.

    This scenario will occur on platforms such as Termux and on some
    more exotic devices.

    https://github.com/python/cpython/blob/4e02981de0952f54bf87967f8e10d169d6946b40/Lib/multiprocessing/synchronize.py#L30-L33
    """
    with mock.patch("multiprocessing.Pool", side_effect=ImportError) as pool:
        result = checker._try_initialize_processpool(2)

    pool.assert_called_once_with(2, checker._pool_init)
    assert result is None
