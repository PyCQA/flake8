"""Tests for the Manager object for FileCheckers."""
import errno
import os

import mock
import pytest

from flake8 import checker


def style_guide_mock(**kwargs):
    """Create a mock StyleGuide object."""
    kwargs.setdefault('diff', False)
    kwargs.setdefault('jobs', '4')
    style_guide = mock.Mock()
    style_guide.options = mock.Mock(**kwargs)
    return style_guide


def test_oserrors_cause_serial_fall_back():
    """Verify that OSErrors will cause the Manager to fallback to serial."""
    err = OSError(errno.ENOSPC, 'Ominous message about spaceeeeee')
    style_guide = style_guide_mock()
    with mock.patch('_multiprocessing.SemLock', side_effect=err):
        manager = checker.Manager(style_guide, [], [])
        with mock.patch.object(manager, 'run_serial') as serial:
                manager.run()
    assert serial.call_count == 1
    assert manager.using_multiprocessing is False


@mock.patch('flake8.utils.is_windows', return_value=False)
def test_oserrors_are_reraised(is_windows):
    """Verify that unexpected OSErrors will cause the Manager to reraise."""
    err = OSError(errno.EAGAIN, 'Ominous message')
    style_guide = style_guide_mock()
    with mock.patch('_multiprocessing.SemLock', side_effect=err):
        with pytest.raises(OSError):
            manager = checker.Manager(style_guide, [], [])
            with mock.patch.object(manager, 'run_serial') as serial:
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

    for file_checker in manager.checkers:
        assert file_checker.filename in files


def test_make_checkers_shebang():
    """Verify that extension-less files with a Python shebang are checked."""
    style_guide = style_guide_mock(
        filename=[],
        exclude=[],
    )
    checkplugins = mock.Mock()
    checkplugins.to_dictionary.return_value = {
        'ast_plugins': [],
        'logical_line_plugins': [],
        'physical_line_plugins': [],
    }
    with mock.patch('flake8.checker.multiprocessing', None):
        manager = checker.Manager(style_guide, [], checkplugins)

    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'fixtures')
    )
    manager.make_checkers([path])

    filenames = [
        os.path.relpath(file_checker.filename, path)
        for file_checker in manager.checkers
    ]
    assert 'example-code/script' in filenames


def test_make_checkers_explicit_pattern_ignore_shebang():
    """Verify that shebangs are ignored when passing a pattern."""
    style_guide = style_guide_mock(
        filename=['*.py'],
        exclude=[],
    )
    checkplugins = mock.Mock()
    checkplugins.to_dictionary.return_value = {
        'ast_plugins': [],
        'logical_line_plugins': [],
        'physical_line_plugins': [],
    }
    with mock.patch('flake8.checker.multiprocessing', None):
        manager = checker.Manager(style_guide, [], checkplugins)

    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'fixtures')
    )
    manager.make_checkers([path])

    filenames = [
        os.path.relpath(file_checker.filename, path)
        for file_checker in manager.checkers
    ]
    assert 'example-code/script' not in filenames
