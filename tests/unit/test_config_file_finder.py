"""Tests for the ConfigFileFinder."""
import os
import sys

import mock

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
    cli_filepath = 'tests/fixtures/config_files/cli-specified.ini'
    finder = config.ConfigFileFinder('flake8', None, [])

    parsed_config = finder.cli_config(cli_filepath)
    assert parsed_config.has_section('flake8')
