"""Tests for the Application class."""
import optparse

import mock
import pytest

from flake8 import exceptions
from flake8.main import application as app


def options(**kwargs):
    """Generate optparse.Values for our Application."""
    kwargs.setdefault('verbose', 0)
    kwargs.setdefault('output_file', None)
    kwargs.setdefault('count', False)
    kwargs.setdefault('exit_zero', False)
    return optparse.Values(kwargs)


@pytest.fixture
def mocked_application():
    """Create an application with a mocked OptionManager."""
    with mock.patch('flake8.options.manager.OptionManager') as optionmanager:
        optmgr = optionmanager.return_value = mock.Mock()
        optmgr.parse_known_args.return_value = (options(), [])
        application = app.Application()

    return application


@pytest.mark.parametrize(
    'result_count, catastrophic, exit_zero', [
        (0, True, True),
        (2, False, True),
        (2, True, True),
    ]
)
def test_exit_does_not_raise(result_count, catastrophic, exit_zero,
                             mocked_application):
    """Verify Application.exit doesn't raise SystemExit."""
    mocked_application.result_count = result_count
    mocked_application.catastrophic_failure = catastrophic
    mocked_application.options = options(exit_zero=exit_zero)

    assert mocked_application.exit() is None


@pytest.mark.parametrize(
    'result_count, catastrophic, exit_zero, value', [
        (0, False, False, False),
        (0, True, False, True),
        (2, False, False, True),
        (2, True, False, True),
    ]
)
def test_exit_does_raise(result_count, catastrophic, exit_zero, value,
                         mocked_application):
    """Verify Application.exit doesn't raise SystemExit."""
    mocked_application.result_count = result_count
    mocked_application.catastrophic_failure = catastrophic
    mocked_application.options = options(exit_zero=exit_zero)

    with pytest.raises(SystemExit) as excinfo:
        mocked_application.exit()

    assert excinfo.value.args[0] is value


def test_missing_default_formatter(mocked_application):
    """Verify we raise an ExecutionError when there's no default formatter."""
    mocked_application.formatting_plugins = {}

    with pytest.raises(exceptions.ExecutionError):
        mocked_application.formatter_for('fake-plugin-name')


def test_warns_on_unknown_formatter_plugin_name(mocked_application):
    """Verify we log a warning with an unfound plugin."""
    default = mock.Mock()
    execute = default.execute
    mocked_application.formatting_plugins = {
        'default': default,
    }
    with mock.patch.object(app.LOG, 'warning') as warning:
        assert execute is mocked_application.formatter_for('fake-plugin-name')

    assert warning.called is True
    assert warning.call_count == 1


def test_returns_specified_plugin(mocked_application):
    """Verify we get the plugin we want."""
    desired = mock.Mock()
    execute = desired.execute
    mocked_application.formatting_plugins = {
        'default': mock.Mock(),
        'desired': desired,
    }

    with mock.patch.object(app.LOG, 'warning') as warning:
        assert execute is mocked_application.formatter_for('desired')

    assert warning.called is False
