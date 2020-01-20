# -*- coding: utf-8 -*-
"""Tests for the ConfigFileFinder."""
import configparser
import os

import mock
import pytest

from flake8.options import config

CLI_SPECIFIED_FILEPATH = 'tests/fixtures/config_files/cli-specified.ini'
BROKEN_CONFIG_PATH = 'tests/fixtures/config_files/broken.ini'


def test_cli_config():
    """Verify opening and reading the file specified via the cli."""
    cli_filepath = CLI_SPECIFIED_FILEPATH
    finder = config.ConfigFileFinder('flake8')

    parsed_config = finder.cli_config(cli_filepath)
    assert parsed_config.has_section('flake8')


@pytest.mark.parametrize('cwd,expected', [
    # Root directory of project
    (os.path.abspath('.'),
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Subdirectory of project directory
    (os.path.abspath('src'),
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Outside of project directory
    (os.path.abspath('/'),
        []),
])
def test_generate_possible_local_files(cwd, expected):
    """Verify generation of all possible config paths."""
    finder = config.ConfigFileFinder('flake8')

    with mock.patch.object(os, 'getcwd', return_value=cwd):
        config_files = list(finder.generate_possible_local_files())

    assert config_files == expected


@pytest.mark.parametrize('extra_config_files,expected', [
    # Extra config files specified
    ([CLI_SPECIFIED_FILEPATH],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini'),
            os.path.abspath(CLI_SPECIFIED_FILEPATH)]),
    # Missing extra config files specified
    ([CLI_SPECIFIED_FILEPATH,
        'tests/fixtures/config_files/missing.ini'],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini'),
            os.path.abspath(CLI_SPECIFIED_FILEPATH)]),
])
def test_local_config_files(extra_config_files, expected):
    """Verify discovery of local config files."""
    finder = config.ConfigFileFinder('flake8', extra_config_files)

    assert list(finder.local_config_files()) == expected


def test_local_configs():
    """Verify we return a ConfigParser."""
    finder = config.ConfigFileFinder('flake8')

    assert isinstance(finder.local_configs(), configparser.RawConfigParser)


@pytest.mark.parametrize('files', [
    [BROKEN_CONFIG_PATH],
    [CLI_SPECIFIED_FILEPATH, BROKEN_CONFIG_PATH],
])
def test_read_config_catches_broken_config_files(files):
    """Verify that we do not allow the exception to bubble up."""
    _, parsed = config.ConfigFileFinder._read_config(*files)
    assert BROKEN_CONFIG_PATH not in parsed


def test_read_config_catches_decoding_errors(tmpdir):
    """Verify that we do not allow the exception to bubble up."""
    setup_cfg = tmpdir.join('setup.cfg')
    # pick bytes that are unlikely to decode
    setup_cfg.write_binary(b'[x]\ny = \x81\x8d\x90\x9d')
    _, parsed = config.ConfigFileFinder._read_config(setup_cfg.strpath)
    assert parsed == []


def test_config_file_default_value():
    """Verify the default 'config_file' attribute value."""
    finder = config.ConfigFileFinder('flake8')
    assert finder.config_file is None


def test_setting_config_file_value():
    """Verify the 'config_file' attribute matches constructed value."""
    config_file_value = 'flake8.ini'
    finder = config.ConfigFileFinder('flake8', config_file=config_file_value)
    assert finder.config_file == config_file_value


def test_ignore_config_files_default_value():
    """Verify the default 'ignore_config_files' attribute value."""
    finder = config.ConfigFileFinder('flake8')
    assert finder.ignore_config_files is False


@pytest.mark.parametrize('ignore_config_files_arg', [
    False,
    True,
])
def test_setting_ignore_config_files_value(ignore_config_files_arg):
    """Verify the 'ignore_config_files' attribute matches constructed value."""
    finder = config.ConfigFileFinder(
        'flake8',
        ignore_config_files=ignore_config_files_arg
    )
    assert finder.ignore_config_files is ignore_config_files_arg
