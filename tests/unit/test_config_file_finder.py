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


def test_uses_default_args():
    """Show that we default the args value."""
    finder = config.ConfigFileFinder('flake8', [], [])
    assert finder.parent == os.path.abspath('.')


@pytest.mark.parametrize('platform,is_windows', [
    ('win32', True),
    ('linux', False),
    ('darwin', False),
])
def test_windows_detection(platform, is_windows):
    """Verify we detect Windows to the best of our knowledge."""
    with mock.patch.object(sys, 'platform', platform):
        finder = config.ConfigFileFinder('flake8', [], [])
    assert finder.is_windows is is_windows


def test_cli_config():
    """Verify opening and reading the file specified via the cli."""
    cli_filepath = CLI_SPECIFIED_FILEPATH
    finder = config.ConfigFileFinder('flake8', [], [])

    parsed_config = finder.cli_config(cli_filepath)
    assert parsed_config.has_section('flake8')


def test_cli_config_double_read():
    """Second request for CLI config is cached."""
    finder = config.ConfigFileFinder('flake8', [], [])

    parsed_config = finder.cli_config(CLI_SPECIFIED_FILEPATH)
    boom = Exception("second request for CLI config not cached")
    with mock.patch.object(finder, '_read_config', side_effect=boom):
        parsed_config_2 = finder.cli_config(CLI_SPECIFIED_FILEPATH)

    assert parsed_config is parsed_config_2


@pytest.mark.parametrize('args,expected', [
    # No arguments, common prefix of abspath('.')
    ([],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Common prefix of "flake8/"
    (['flake8/options', 'flake8/'],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Common prefix of "flake8/options"
    (['flake8/options', 'flake8/options/sub'],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
])
def test_generate_possible_local_files(args, expected):
    """Verify generation of all possible config paths."""
    finder = config.ConfigFileFinder('flake8', args, [])

    assert (list(finder.generate_possible_local_files())
            == expected)


@pytest.mark.parametrize('args,extra_config_files,expected', [
    # No arguments, common prefix of abspath('.')
    ([],
        [],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Common prefix of "flake8/"
    (['flake8/options', 'flake8/'],
        [],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Common prefix of "flake8/options"
    (['flake8/options', 'flake8/options/sub'],
        [],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini')]),
    # Common prefix of "flake8/" with extra config files specified
    (['flake8/'],
        [CLI_SPECIFIED_FILEPATH],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini'),
            os.path.abspath(CLI_SPECIFIED_FILEPATH)]),
    # Common prefix of "flake8/" with missing extra config files specified
    (['flake8/'],
        [CLI_SPECIFIED_FILEPATH,
            'tests/fixtures/config_files/missing.ini'],
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini'),
            os.path.abspath(CLI_SPECIFIED_FILEPATH)]),
])
def test_local_config_files(args, extra_config_files, expected):
    """Verify discovery of local config files."""
    finder = config.ConfigFileFinder('flake8', args, extra_config_files)

    assert list(finder.local_config_files()) == expected


def test_local_configs():
    """Verify we return a ConfigParser."""
    finder = config.ConfigFileFinder('flake8', [], [])

    assert isinstance(finder.local_configs(), configparser.RawConfigParser)


def test_local_configs_double_read():
    """Second request for local configs is cached."""
    finder = config.ConfigFileFinder('flake8', [], [])

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
    _, parsed = config.ConfigFileFinder._read_config(files)
    assert BROKEN_CONFIG_PATH not in parsed


def test_read_config_catches_decoding_errors(tmpdir):
    """Verify that we do not allow the exception to bubble up."""
    setup_cfg = tmpdir.join('setup.cfg')
    # pick bytes that are unlikely to decode
    setup_cfg.write_binary(b'[x]\ny = \x81\x8d\x90\x9d')
    _, parsed = config.ConfigFileFinder._read_config(setup_cfg.strpath)
    assert parsed == []
