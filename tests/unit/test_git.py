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
