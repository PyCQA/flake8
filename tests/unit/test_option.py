"""Unit tests for flake8.options.manager.Option."""
import functools
from unittest import mock

import pytest

from flake8.options import manager


def test_to_argparse():
    """Test conversion to an argparse arguments."""
    opt = manager.Option(
        short_option_name="-t",
        long_option_name="--test",
        action="count",
        parse_from_config=True,
        normalize_paths=True,
    )
    assert opt.normalize_paths is True
    assert opt.parse_from_config is True

    args, kwargs = opt.to_argparse()
    assert args == ["-t", "--test"]
    assert kwargs == {"action": "count", "type": mock.ANY}
    assert isinstance(kwargs["type"], functools.partial)


def test_to_argparse_creates_an_option_as_we_expect():
    """Show that we pass all keyword args to argparse."""
    opt = manager.Option("-t", "--test", action="count")
    args, kwargs = opt.to_argparse()
    assert args == ["-t", "--test"]
    assert kwargs == {"action": "count"}


def test_config_name_generation():
    """Show that we generate the config name deterministically."""
    opt = manager.Option(
        long_option_name="--some-very-long-option-name",
        parse_from_config=True,
    )

    assert opt.config_name == "some_very_long_option_name"


def test_config_name_needs_long_option_name():
    """Show that we error out if the Option should be parsed from config."""
    with pytest.raises(ValueError):
        manager.Option("-s", parse_from_config=True)


def test_dest_is_not_overridden():
    """Show that we do not override custom destinations."""
    opt = manager.Option("-s", "--short", dest="something_not_short")
    assert opt.dest == "something_not_short"
