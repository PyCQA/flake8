"""Tests for the Manager object for FileCheckers."""
import errno

import mock
import pytest

from flake8 import checker
from flake8.main.options import JobsArgument


def style_guide_mock():
    """Create a mock StyleGuide object."""
    return mock.MagicMock(**{
        'options.diff': False,
        'options.jobs': JobsArgument("4"),
    })


def _parallel_checker_manager():
    """Call Manager.run() and return the number of calls to `run_serial`."""
    style_guide = style_guide_mock()
    manager = checker.Manager(style_guide, [], [])
    # multiple checkers is needed for parallel mode
    manager.checkers = [mock.Mock(), mock.Mock()]
    return manager


def test_oserrors_cause_serial_fall_back():
    """Verify that OSErrors will cause the Manager to fallback to serial."""
    err = OSError(errno.ENOSPC, 'Ominous message about spaceeeeee')
    with mock.patch('_multiprocessing.SemLock', side_effect=err):
        manager = _parallel_checker_manager()
        with mock.patch.object(manager, 'run_serial') as serial:
            manager.run()
    assert serial.call_count == 1


@mock.patch('flake8.checker._multiprocessing_is_fork', return_value=True)
def test_oserrors_are_reraised(is_windows):
    """Verify that unexpected OSErrors will cause the Manager to reraise."""
    err = OSError(errno.EAGAIN, 'Ominous message')
    with mock.patch('_multiprocessing.SemLock', side_effect=err):
        manager = _parallel_checker_manager()
        with mock.patch.object(manager, 'run_serial') as serial:
            with pytest.raises(OSError):
                manager.run()
    assert serial.call_count == 0


def test_multiprocessing_is_disabled():
    """Verify not being able to import multiprocessing forces jobs to 0."""
    style_guide = style_guide_mock()
    with mock.patch('flake8.checker.multiprocessing', None):
        manager = checker.Manager(style_guide, [], [])
        assert manager.jobs == 0


def test_make_checkers():
    """Verify that we create a list of FileChecker instances."""
    style_guide = style_guide_mock()
    files = ['file1', 'file2']
    checkplugins = mock.Mock()
    checkplugins.to_dictionary.return_value = {
        'ast_plugins': [],
        'logical_line_plugins': [],
        'physical_line_plugins': [],
    }
    with mock.patch('flake8.checker.multiprocessing', None):
        manager = checker.Manager(style_guide, files, checkplugins)

    with mock.patch('flake8.utils.filenames_from') as filenames_from:
        filenames_from.side_effect = [['file1'], ['file2']]
        with mock.patch('flake8.utils.fnmatch', return_value=True):
            with mock.patch('flake8.processor.FileProcessor'):
                manager.make_checkers()

    assert manager._all_checkers
    for file_checker in manager._all_checkers:
        assert file_checker.filename in files
    assert not manager.checkers  # the files don't exist
