"""Unit tests for flake8.options.config.MergedConfigParser."""
import os

import mock
import pytest

from flake8.options import config
from flake8.options import manager


@pytest.fixture
def optmanager():
    return manager.OptionManager(prog='flake8', version='3.0.0a1')


@pytest.mark.parametrize('args,extra_config_files', [
    (None, None),
    (None, []),
    (None, ['foo.ini']),
    ('flake8/', []),
    ('flake8/', ['foo.ini']),
])
def test_creates_its_own_config_file_finder(args, extra_config_files,
                                            optmanager):
    """Verify we create a ConfigFileFinder correctly."""
    class_path = 'flake8.options.config.ConfigFileFinder'
    with mock.patch(class_path) as ConfigFileFinder:
        parser = config.MergedConfigParser(
            option_manager=optmanager,
            extra_config_files=extra_config_files,
            args=args,
        )

    assert parser.program_name == 'flake8'
    ConfigFileFinder.assert_called_once_with(
        'flake8',
        args,
        extra_config_files or [],
    )


def test_parse_cli_config(optmanager):
    """Parse the specified config file as a cli config file."""
    optmanager.add_option('--exclude', parse_from_config=True,
                          comma_separated_list=True,
                          normalize_paths=True)
    optmanager.add_option('--ignore', parse_from_config=True,
                          comma_separated_list=True)
    parser = config.MergedConfigParser(optmanager)

    parsed_config = parser.parse_cli_config(
        'tests/fixtures/config_files/cli-specified.ini'
    )
    assert parsed_config == {
        'ignore': ['E123', 'W234', 'E111'],
        'exclude': [
            os.path.abspath('foo/'),
            os.path.abspath('bar/'),
            os.path.abspath('bogus/'),
        ]
    }
