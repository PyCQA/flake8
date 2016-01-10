"""Tests for the ConfigFileFinder."""
import os

from flake8.options import config


def test_uses_default_args():
    """Show that we default the args value."""
    finder = config.ConfigFileFinder('flake8', None, [])
    assert finder.args == ['.']
    assert finder.parent == os.path.abspath('.')
