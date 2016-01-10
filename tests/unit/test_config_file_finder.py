"""Tests for the ConfigFileFinder."""
import os
import sys

import mock
import pytest

from flake8.options import config


def test_uses_default_args():
    """Show that we default the args value."""
    finder = config.ConfigFileFinder('flake8', None, [])
    assert finder.parent == os.path.abspath('.')


@mock.patch.object(sys, 'platform', 'win32')
def test_windows_detection():
    """Verify we detect Windows to the best of our knowledge."""
    finder = config.ConfigFileFinder('flake8', None, [])
    assert finder.is_windows is True


def test_cli_config():
    """Verify opening and reading the file specified via the cli."""
    cli_filepath = 'tests/fixtures/config_files/cli-specified.ini'
    finder = config.ConfigFileFinder('flake8', None, [])

    parsed_config = finder.cli_config(cli_filepath)
    assert parsed_config.has_section('flake8')


@pytest.mark.parametrize('args,expected', [
    ([],  # No arguments
        [os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini'),
            os.path.abspath('.flake8')]),
    (['flake8/options', 'flake8/'],  # Common prefix of "flake8/"
        [os.path.abspath('flake8/setup.cfg'),
            os.path.abspath('flake8/tox.ini'),
            os.path.abspath('flake8/.flake8'),
            os.path.abspath('setup.cfg'),
            os.path.abspath('tox.ini'),
            os.path.abspath('.flake8')]),
])
def test_generate_possible_local_config_files(args, expected):
    """Verify generation of all possible config paths."""
    finder = config.ConfigFileFinder('flake8', args, [])

    assert (list(finder.generate_possible_local_config_files()) ==
            expected)
