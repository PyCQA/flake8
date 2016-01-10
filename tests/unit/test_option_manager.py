"""Unit tests for flake.options.manager.OptionManager."""
import optparse
import os

import pytest

from flake8.options import manager


@pytest.fixture
def optmanager():
    """Generate a simple OptionManager with default test arguments."""
    return manager.OptionManager(prog='flake8', version='3.0.0b1')


def test_option_manager_creates_option_parser(optmanager):
    """Verify that a new manager creates a new parser."""
    assert optmanager.parser is not None
    assert isinstance(optmanager.parser, optparse.OptionParser) is True


def test_add_option_short_option_only(optmanager):
    """Verify the behaviour of adding a short-option only."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('-s', help='Test short opt')
    assert optmanager.options[0].short_option_name == '-s'


def test_add_option_long_option_only(optmanager):
    """Verify the behaviour of adding a long-option only."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--long', help='Test long opt')
    assert optmanager.options[0].short_option_name is None
    assert optmanager.options[0].long_option_name == '--long'


def test_add_short_and_long_option_names(optmanager):
    """Verify the behaviour of using both short and long option names."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('-b', '--both', help='Test both opts')
    assert optmanager.options[0].short_option_name == '-b'
    assert optmanager.options[0].long_option_name == '--both'


def test_add_option_with_custom_args(optmanager):
    """Verify that add_option handles custom Flake8 parameters."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--parse', parse_from_config=True)
    optmanager.add_option('--commas', comma_separated_list=True)
    optmanager.add_option('--files', normalize_paths=True)

    attrs = ['parse_from_config', 'comma_separated_list', 'normalize_paths']
    for option, attr in zip(optmanager.options, attrs):
        assert getattr(option, attr) is True


def test_parse_args_normalize_path(optmanager):
    """Show that parse_args handles path normalization."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--config', normalize_paths=True)

    options, args = optmanager.parse_args(['--config', '../config.ini'])
    assert options.config == os.path.abspath('../config.ini')


def test_parse_args_handles_comma_separated_defaults(optmanager):
    """Show that parse_args handles defaults that are comma-separated."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--exclude', default='E123,W234',
                          comma_separated_list=True)

    options, args = optmanager.parse_args([])
    assert options.exclude == ['E123', 'W234']


def test_parse_args_handles_comma_separated_lists(optmanager):
    """Show that parse_args handles user-specified comma-separated lists."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--exclude', default='E123,W234',
                          comma_separated_list=True)

    options, args = optmanager.parse_args(['--exclude', 'E201,W111,F280'])
    assert options.exclude == ['E201', 'W111', 'F280']


def test_parse_args_normalize_paths(optmanager):
    """Verify parse_args normalizes a comma-separated list of paths."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--extra-config', normalize_paths=True,
                          comma_separated_list=True)

    options, args = optmanager.parse_args([
        '--extra-config', '../config.ini,tox.ini,flake8/some-other.cfg'
    ])
    assert options.extra_config == [
        os.path.abspath('../config.ini'),
        'tox.ini',
        os.path.abspath('flake8/some-other.cfg'),
    ]
