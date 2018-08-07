"""Test aggregation of config files and command-line options."""
import os

import mock
import pytest

from flake8 import defaults
from flake8.main import options
from flake8.options import aggregator
from flake8.options import config
from flake8.options import manager

CLI_SPECIFIED_CONFIG = 'tests/fixtures/config_files/cli-specified.ini'
USER_CONFIG = 'tests/fixtures/config_files/user-config.ini'
LOCAL_CONFIG = 'tests/fixtures/config_files/local-config.ini'
MISSING_CONFIG = 'tests/fixtures/config_files/missing.ini'


@pytest.fixture
def optmanager():
    """Create a new OptionManager."""
    option_manager = manager.OptionManager(
        prog='flake8',
        version='3.0.0',
    )
    options.register_default_options(option_manager)
    return option_manager


def mock_config_finder(program='flake8', arguments=[],
                       prepend_configs=[], append_configs=[],
                       user_config='', local_configs=[]):
    """Create a config finder with controlled access to files."""
    config_finder = config.ConfigFileFinder(
        program, arguments, prepend_configs, append_configs)

    config_finder.user_config_file = mock.Mock(return_value=user_config)
    config_finder.generate_possible_local_files = mock.Mock(
        return_value=local_configs
    )

    return config_finder


@pytest.mark.parametrize('config_finder_params,options_assertions', [
    # Default values with no config file
    ({}, {
        "select": {'E', 'W', 'F', 'C90'},
        "ignore": set(defaults.IGNORE),
        "max_line_length": 79,
    }),
    # Correct values with user config only
    ({'user_config': USER_CONFIG}, {
        "select": {'E', 'W', 'F', 'C90'},
        "ignore": ['D203'],
        "max_line_length": 79,
    }),
    # Default values with missing user config file
    ({'user_config': MISSING_CONFIG}, {
        "select": {'E', 'W', 'F', 'C90'},
        "ignore": set(defaults.IGNORE),
        "max_line_length": 79,
    }),
    # Correct values with local config only
    ({'local_configs': [LOCAL_CONFIG]}, {
        "select": {'E', 'W', 'F'},
        "ignore": set(defaults.IGNORE),
        "max_line_length": 79,
    }),
    # Default values with missing local config file
    ({'local_configs': [MISSING_CONFIG]}, {
        "select": {'E', 'W', 'F', 'C90'},
        "ignore": set(defaults.IGNORE),
        "max_line_length": 79,
    }),
])
def test_aggregate_options_resulting_values(
        optmanager, config_finder_params, options_assertions
):
    """Verify we get correct values with various config files combinations."""
    arguments = []
    config_finder = mock_config_finder(**config_finder_params)
    parsed_options, args = aggregator.aggregate_options(
        optmanager, config_finder, arguments
    )

    for option, expected_value in options_assertions.items():
        # Cast the option to the expected value type, especially for sets
        expected_type = type(expected_value)
        option_value = getattr(parsed_options, option)
        assert expected_value == expected_type(option_value)


def test_aggregate_options_with_config(optmanager):
    """Verify we aggregate options and config values appropriately."""
    arguments = ['flake8', '--config', CLI_SPECIFIED_CONFIG, '--select',
                 'E11,E34,E402,W,F', '--exclude', 'tests/*']
    config_finder = config.ConfigFileFinder('flake8', arguments, [], [])
    options, args = aggregator.aggregate_options(
        optmanager, config_finder, arguments)

    assert options.config == CLI_SPECIFIED_CONFIG
    assert options.select == ['E11', 'E34', 'E402', 'W', 'F']
    assert options.ignore == ['E123', 'W234', 'E111']
    assert options.exclude == [os.path.abspath('tests/*')]


def test_aggregate_options_when_isolated(optmanager):
    """Verify we aggregate options and config values appropriately."""
    arguments = ['flake8', '--isolated', '--select', 'E11,E34,E402,W,F',
                 '--exclude', 'tests/*']
    config_finder = config.ConfigFileFinder('flake8', arguments, [], [])
    optmanager.extend_default_ignore(['E8'])
    options, args = aggregator.aggregate_options(
        optmanager, config_finder, arguments)

    assert options.isolated is True
    assert options.select == ['E11', 'E34', 'E402', 'W', 'F']
    assert sorted(options.ignore) == [
        'E121', 'E123', 'E126', 'E226', 'E24', 'E704', 'E8', 'W503', 'W504',
    ]
    assert options.exclude == [os.path.abspath('tests/*')]
