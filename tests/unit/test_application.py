"""Tests for the Application class."""
import argparse
import sys

import mock
import pytest

from flake8.main import application as app


def options(**kwargs):
    """Generate argparse.Namespace for our Application."""
    kwargs.setdefault('verbose', 0)
    kwargs.setdefault('output_file', None)
    kwargs.setdefault('count', False)
    kwargs.setdefault('exit_zero', False)
    return argparse.Namespace(**kwargs)


@pytest.fixture
def application():
    """Create an application."""
    return app.Application()


@pytest.mark.parametrize(
    'result_count, catastrophic, exit_zero, value', [
        (0, False, False, False),
        (0, True, False, True),
        (2, False, False, True),
        (2, True, False, True),

        (0, True, True, True),
        (2, False, True, False),
        (2, True, True, True),
    ]
)
def test_exit_does_raise(result_count, catastrophic, exit_zero, value,
                         application):
    """Verify Application.exit doesn't raise SystemExit."""
    application.result_count = result_count
    application.catastrophic_failure = catastrophic
    application.options = options(exit_zero=exit_zero)

    with pytest.raises(SystemExit) as excinfo:
        application.exit()

    assert excinfo.value.args[0] is value


def test_warns_on_unknown_formatter_plugin_name(application):
    """Verify we log a warning with an unfound plugin."""
    default = mock.Mock()
    execute = default.execute
    application.formatting_plugins = {
        'default': default,
    }
    with mock.patch.object(app.LOG, 'warning') as warning:
        assert execute is application.formatter_for('fake-plugin-name')

    assert warning.called is True
    assert warning.call_count == 1


def test_returns_specified_plugin(application):
    """Verify we get the plugin we want."""
    desired = mock.Mock()
    execute = desired.execute
    application.formatting_plugins = {
        'default': mock.Mock(),
        'desired': desired,
    }

    with mock.patch.object(app.LOG, 'warning') as warning:
        assert execute is application.formatter_for('desired')

    assert warning.called is False


def test_prelim_opts_args(application):
    """Verify we get sensible prelim opts and args."""
    opts, args = application.parse_preliminary_options(
        ['--foo', '--verbose', 'src', 'setup.py', '--statistics', '--version'])

    assert opts.verbose
    assert args == ['--foo', 'src', 'setup.py', '--statistics', '--version']


def test_prelim_opts_ignore_help(application):
    """Verify -h/--help is not handled."""
    # GIVEN

    # WHEN
    _, args = application.parse_preliminary_options(['--help', '-h'])

    # THEN
    assert args == ['--help', '-h']


def test_prelim_opts_handles_empty(application):
    """Verify empty argv lists are handled correctly."""
    irrelevant_args = ['myexe', '/path/to/foo']
    with mock.patch.object(sys, 'argv', irrelevant_args):
        opts, args = application.parse_preliminary_options([])

        assert args == []
