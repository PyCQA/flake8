"""Unit tests for the FileChecker class."""
import mock

from flake8 import checker


@mock.patch('flake8.processor.FileProcessor')
def test_run_ast_checks_handles_SyntaxErrors(FileProcessor):
    """Stress our SyntaxError handling.

    Related to: https://gitlab.com/pycqa/flake8/issues/237
    """
    processor = mock.Mock(lines=[])
    FileProcessor.return_value = processor
    processor.build_ast.side_effect = SyntaxError('Failed to build ast',
                                                  ('', 1, 5, 'foo(\n'))
    file_checker = checker.FileChecker(__file__, checks={}, options=object())

    with mock.patch.object(file_checker, 'report') as report:
        file_checker.run_ast_checks()

        report.assert_called_once_with(
            'E999', 1, 3,
            'SyntaxError: Failed to build ast',
        )


@mock.patch('flake8.checker.FileChecker._make_processor', return_value=None)
def test_repr(*args):
    """Verify we generate a correct repr."""
    file_checker = checker.FileChecker(
        'example.py', checks={}, options=object(),
    )
    assert repr(file_checker) == 'FileChecker for example.py'
