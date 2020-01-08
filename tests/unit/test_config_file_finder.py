# -*- coding: utf-8 -*-
"""Tests for the ConfigFileFinder."""
import configparser
import os
import sys

import mock
import pytest

from flake8.options import config

CLI_SPECIFIED_FILEPATH = 'tests/fixtures/config_files/cli-specified.ini'
BROKEN_CONFIG_PATH = 'tests/fixtures/config_files/broken.ini'


@pytest.mark.parametrize('platform,is_windows', [
    ('win32', True),
    ('linux', False),
    ('darwin', False),
])
def test_windows_detection(platform, is_windows):
    """Verify we detect Windows to the best of our knowledge."""
    with mock.patch.object(sys, 'platform', platform):
        finder = config.ConfigFileFinder('flake8', [])
    assert finder.is_windows is is_windows


def test_cli_config():
    """Verify opening and reading the file specified via the cli."""
    cli_filepath = CLI_SPECIFIED_FILEPATH
    finder = config.ConfigFileFinder('flake8', [])

    parsed_config = finder.cli_config(cli_filepath)
    assert parsed_config.has_section('flake8')


def test_cli_config_double_read():
    """Second request for CLI config is cached."""
    finder = config.ConfigFileFinder('flake8', [])

    parsed_config = finder.cli_config(CLI_SPECIFIED_FILEPATH)
    boom = Exception("second request for CLI config not cached")
    with mock.patch.object(finder, '_read_config', side_effect=boom):
        parsed_config_2 = finder.cli_config(CLI_SPECIFIED_FILEPATH)

    assert parsed_config is parsed_config_2


@pytest.mark.parametrize('cwd,expected', [
    # Root directory of project
    ('.',
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Subdirectory of project directory
    ('src',
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Outside of project directory
    ('/',
        []),
])
def test_generate_possible_local_files(cwd, expected):
    """Verify generation of all possible config paths."""
    with mock.patch.object(os, 'getcwd', return_value=cwd):
        finder = config.ConfigFileFinder('flake8', [])

    assert (list(finder.generate_possible_local_files())
            == expected)


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
    finder = config.ConfigFileFinder('flake8', [])

    assert isinstance(finder.local_configs(), configparser.RawConfigParser)


def test_local_configs_double_read():
    """Second request for local configs is cached."""
    finder = config.ConfigFileFinder('flake8', [])

    first_read = finder.local_configs()
    boom = Exception("second request for local configs not cached")
    with mock.patch.object(finder, '_read_config', side_effect=boom):
        second_read = finder.local_configs()

    assert first_read is second_read


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


def test_ignore_config_files_default_value():
    """Verify the default 'ignore_config_files' attribute value."""
    finder = config.ConfigFileFinder('flake8', [])
    assert finder.ignore_config_files is False


@pytest.mark.parametrize('ignore_config_files_arg', [
    False,
    True,
])
def test_setting_ignore_config_files_value(ignore_config_files_arg):
    """Verify the 'ignore_config_files' attribute matches constructed value."""
    finder = config.ConfigFileFinder(
        'flake8',
        [],
        ignore_config_files=ignore_config_files_arg
    )
    assert finder.ignore_config_files is ignore_config_files_arg
