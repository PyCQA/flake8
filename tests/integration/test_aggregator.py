"""Test aggregation of config files and command-line options."""
import os

import pytest

from flake8.main import options
from flake8.options import aggregator
from flake8.options import config
from flake8.options import manager

CLI_SPECIFIED_CONFIG = 'tests/fixtures/config_files/cli-specified.ini'


@pytest.fixture
def optmanager():
    """Create a new OptionManager."""
    option_manager = manager.OptionManager(
        prog='flake8',
        version='3.0.0',
    )
    options.register_default_options(option_manager)
    return option_manager


def test_aggregate_options_with_config(optmanager):
    """Verify we aggregate options and config values appropriately."""
    arguments = ['flake8', '--config', CLI_SPECIFIED_CONFIG, '--select',
                 'E11,E34,E402,W,F', '--exclude', 'tests/*']
    config_finder = config.ConfigFileFinder('flake8', arguments, [])
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
    config_finder = config.ConfigFileFinder('flake8', arguments, [])
    optmanager.extend_default_ignore(['E8'])
    options, args = aggregator.aggregate_options(
        optmanager, config_finder, arguments)

    assert options.isolated is True
    assert options.select == ['E11', 'E34', 'E402', 'W', 'F']
    assert sorted(options.ignore) == [
        'E121', 'E123', 'E126', 'E226', 'E24', 'E704', 'E8', 'W503', 'W504',
    ]
    assert options.exclude == [os.path.abspath('tests/*')]
