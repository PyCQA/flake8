"""Tests around functionality in the git integration."""
import mock
import pytest

from flake8.main import git


@pytest.mark.parametrize('lazy', [True, False])
def test_find_modified_files(lazy):
    """Confirm our logic for listing modified files."""
    if lazy:
        # Here --cached is missing
        call = [
            'git', 'diff-index', '--name-only', '--diff-filter=ACMRTUXB',
            'HEAD'
        ]
    else:
        call = [
            'git', 'diff-index', '--cached', '--name-only',
            '--diff-filter=ACMRTUXB', 'HEAD'
        ]
    mocked_popen = mock.Mock()
    mocked_popen.communicate.return_value = ('', '')

    with mock.patch('flake8.main.git.piped_process') as piped_process:
        piped_process.return_value = mocked_popen
        git.find_modified_files(lazy)

    piped_process.assert_called_once_with(call)


@mock.patch("flake8.main.git.copy_indexed_files_to")
@mock.patch("flake8.checker.os.path.exists", autospec=True)
@mock.patch("flake8.checker.FileChecker._make_processor", autospec=True)
def test_only_py_files(mock_processor, mock_exists, mock_files):
    """Confirm only run checks on Python source file."""
    class MockProcessor(object):
        def __init__(self, filename):
            self.filename = filename
            self.lines = []

    mock_processor.side_effect = lambda self: MockProcessor(self.filename)
    mock_exists.return_value = True
    mock_files.return_value = [
        "/tmp/xxx/test.py",
        "/tmp/xxx/test.html",
        "/tmp/xxx/test.txt",
    ]

    def _run_to_test_checker(self):
        new_paths = [x.filename for x in self.checkers]
        assert "/tmp/xxx/test.py" in new_paths
        assert "/tmp/xxx/test.html" not in new_paths
        assert "/tmp/xxx/test.txt" not in new_paths

    with mock.patch("flake8.checker.Manager.run", autospec=True) as mock_run:
        mock_run.side_effect = _run_to_test_checker
        git.hook(lazy=False)
