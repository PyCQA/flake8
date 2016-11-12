"""Tests for the Application class."""
import optparse

import mock
import pytest

from flake8.main import application as app


def options(**kwargs):
    """Generate optparse.Values for our Application."""
    kwargs.setdefault('verbose', 0)
    kwargs.setdefault('output_file', None)
    kwargs.setdefault('count', False)
    kwargs.setdefault('exit_zero', False)
    return optparse.Values(kwargs)


@pytest.mark.parametrize(
    'result_count, catastrophic, exit_zero', [
        (0, True, True),
        (2, False, True),
        (2, True, True),
    ]
)
def test_exit_does_not_raise(result_count, catastrophic, exit_zero):
    """Verify Application.exit doesn't raise SystemExit."""
    with mock.patch('flake8.options.manager.OptionManager') as optionmanager:
        optmgr = optionmanager.return_value = mock.Mock()
        optmgr.parse_known_args.return_value = (options(), [])
        application = app.Application()

    application.result_count = result_count
    application.catastrophic_failure = catastrophic
    application.options = options(exit_zero=exit_zero)

    assert application.exit() is None


@pytest.mark.parametrize(
    'result_count, catastrophic, exit_zero, value', [
        (0, False, False, False),
        (0, True, False, True),
        (2, False, False, True),
        (2, True, False, True),
    ]
)
def test_exit_does_raise(result_count, catastrophic, exit_zero, value):
    """Verify Application.exit doesn't raise SystemExit."""
    with mock.patch('flake8.options.manager.OptionManager') as optionmanager:
        optmgr = optionmanager.return_value = mock.Mock()
        optmgr.parse_known_args.return_value = (options(), [])
        application = app.Application()

    application.result_count = result_count
    application.catastrophic_failure = catastrophic
    application.options = options(exit_zero=exit_zero)

    with pytest.raises(SystemExit) as excinfo:
        application.exit()

    assert excinfo.value.args[0] is value
