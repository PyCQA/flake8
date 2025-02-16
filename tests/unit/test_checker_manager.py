"""Tests for the Manager object for FileCheckers."""
from __future__ import annotations

import errno
import multiprocessing
from unittest import mock

import pytest

from flake8 import checker
from flake8.main.options import JobsArgument
from flake8.plugins import finder


def style_guide_mock():
    """Create a mock StyleGuide object."""
    return mock.MagicMock(**{"options.jobs": JobsArgument("4")})


def _parallel_checker_manager():
    """Call Manager.run() and return the number of calls to `run_serial`."""
    style_guide = style_guide_mock()
    manager = checker.Manager(style_guide, finder.Checkers([], [], []), [])
    # multiple files is needed for parallel mode
    manager.filenames = ("file1", "file2")
    return manager


def test_oserrors_cause_serial_fall_back():
    """Verify that OSErrors will cause the Manager to fallback to serial."""
    err = OSError(errno.ENOSPC, "Ominous message about spaceeeeee")
    with mock.patch("_multiprocessing.SemLock", side_effect=err):
        manager = _parallel_checker_manager()
        with mock.patch.object(manager, "run_serial") as serial:
            manager.run()
    assert serial.call_count == 1


def test_oserrors_are_reraised():
    """Verify that unexpected OSErrors will cause the Manager to reraise."""
    err = OSError(errno.EAGAIN, "Ominous message")
    with mock.patch("_multiprocessing.SemLock", side_effect=err):
        manager = _parallel_checker_manager()
        with mock.patch.object(manager, "run_serial") as serial:
            with pytest.raises(OSError):
                manager.run()
    assert serial.call_count == 0


def test_multiprocessing_cpu_count_not_implemented():
    """Verify that jobs is 0 if cpu_count is unavailable."""
    style_guide = style_guide_mock()
    style_guide.options.jobs = JobsArgument("auto")

    with mock.patch.object(
        multiprocessing,
        "cpu_count",
        side_effect=NotImplementedError,
    ):
        manager = checker.Manager(style_guide, finder.Checkers([], [], []), [])
    assert manager.jobs == 0


def test_jobs_count_limited_to_file_count():
    style_guide = style_guide_mock()
    style_guide.options.jobs = JobsArgument("4")
    style_guide.options.filenames = ["file1", "file2"]
    manager = checker.Manager(style_guide, finder.Checkers([], [], []), [])
    assert manager.jobs == 4
    manager.start()
    assert manager.jobs == 2


def test_make_checkers():
    """Verify that we create a list of FileChecker instances."""
    style_guide = style_guide_mock()
    style_guide.options.filenames = ["file1", "file2"]
    manager = checker.Manager(style_guide, finder.Checkers([], [], []), [])
    manager.start()
    assert manager.filenames == ("file1", "file2")
