"""Tests for the Manager object for FileCheckers."""
import errno
import multiprocessing
from unittest import mock

import pytest

from flake8 import checker
from flake8.main.options import JobsArgument
from flake8.plugins import finder


def style_guide_mock():
    """Create a mock StyleGuide object."""
    return mock.MagicMock(
        **{
            "options.diff": False,
            "options.jobs": JobsArgument("4"),
        }
    )


def _parallel_checker_manager():
    """Call Manager.run() and return the number of calls to `run_serial`."""
    style_guide = style_guide_mock()
    manager = checker.Manager(style_guide, finder.Checkers([], [], []))
    # multiple checkers is needed for parallel mode
    manager.checkers = [mock.Mock(), mock.Mock()]
    return manager


def test_oserrors_cause_serial_fall_back():
    """Verify that OSErrors will cause the Manager to fallback to serial."""
    err = OSError(errno.ENOSPC, "Ominous message about spaceeeeee")
    with mock.patch("_multiprocessing.SemLock", side_effect=err):
        manager = _parallel_checker_manager()
        with mock.patch.object(manager, "run_serial") as serial:
            manager.run()
    assert serial.call_count == 1


@mock.patch.object(multiprocessing, "get_start_method", return_value="fork")
def test_oserrors_are_reraised(_):
    """Verify that unexpected OSErrors will cause the Manager to reraise."""
    err = OSError(errno.EAGAIN, "Ominous message")
    with mock.patch("_multiprocessing.SemLock", side_effect=err):
        manager = _parallel_checker_manager()
        with mock.patch.object(manager, "run_serial") as serial:
            with pytest.raises(OSError):
                manager.run()
    assert serial.call_count == 0


@mock.patch.object(multiprocessing, "get_start_method", return_value="spawn")
def test_multiprocessing_is_disabled(_):
    """Verify not being able to import multiprocessing forces jobs to 0."""
    style_guide = style_guide_mock()
    manager = checker.Manager(style_guide, finder.Checkers([], [], []))
    assert manager.jobs == 0


def test_multiprocessing_cpu_count_not_implemented():
    """Verify that jobs is 0 if cpu_count is unavailable."""
    style_guide = style_guide_mock()
    style_guide.options.jobs = JobsArgument("auto")

    with mock.patch.object(
        multiprocessing,
        "cpu_count",
        side_effect=NotImplementedError,
    ):
        manager = checker.Manager(style_guide, finder.Checkers([], [], []))
    assert manager.jobs == 0


@mock.patch.object(multiprocessing, "get_start_method", return_value="spawn")
def test_make_checkers(_):
    """Verify that we create a list of FileChecker instances."""
    style_guide = style_guide_mock()
    style_guide.options.filenames = ["file1", "file2"]
    manager = checker.Manager(style_guide, finder.Checkers([], [], []))

    with mock.patch("flake8.utils.fnmatch", return_value=True):
        with mock.patch("flake8.processor.FileProcessor"):
            manager.make_checkers(["file1", "file2"])

    assert manager._all_checkers
    for file_checker in manager._all_checkers:
        assert file_checker.filename in style_guide.options.filenames
    assert not manager.checkers  # the files don't exist
