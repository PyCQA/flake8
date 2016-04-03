"""Tests for the Manager object for FileCheckers."""
import errno
import mock

import pytest

from flake8 import checker


def test_oserrors_cause_serial_fall_back():
    """Verify that OSErrors will cause the Manager to fallback to serial."""
    err = OSError(errno.ENOSPC, 'Ominous message about spaceeeeee')
    style_guide = mock.Mock()
    style_guide.options = mock.Mock(diff=False, jobs='4')
    with mock.patch('multiprocessing.Queue', side_effect=err):
        manager = checker.Manager(style_guide, [], [])
    assert manager.using_multiprocessing is False


def test_oserrors_are_reraised():
    """Verify that OSErrors will cause the Manager to fallback to serial."""
    err = OSError(errno.EAGAIN, 'Ominous message')
    style_guide = mock.Mock()
    style_guide.options = mock.Mock(diff=False, jobs='4')
    with mock.patch('multiprocessing.Queue', side_effect=err):
        with pytest.raises(OSError):
            checker.Manager(style_guide, [], [])
