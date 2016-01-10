"""Unit tests for flake.options.manager.OptionManager."""
import optparse
import os

import pytest

from flake8.options import manager


@pytest.fixture
def optmanager():
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
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--parse', parse_from_config=True)
    optmanager.add_option('--commas', comma_separated_list=True)
    optmanager.add_option('--files', normalize_paths=True)

    attrs = ['parse_from_config', 'comma_separated_list', 'normalize_paths']
    for option, attr in zip(optmanager.options, attrs):
        assert getattr(option, attr) is True


def test_parse_args_normalize_path(optmanager):
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('-v', '--verbose', action='count')
    optmanager.add_option('--config', normalize_paths=True)
    optmanager.add_option('--exclude', default='E123,W234',
                          comma_separated_list=True)

    options, args = optmanager.parse_args(
        ['-v', '-v', '-v', '--config', '../config.ini']
    )
    assert options.verbose == 3
    assert options.config == os.path.abspath('../config.ini')
    assert options.exclude == ['E123', 'W234']
