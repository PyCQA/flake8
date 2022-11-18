"""Unit tests for flake.options.manager.OptionManager."""
from __future__ import annotations

import argparse
import os

import pytest

from flake8.main.options import JobsArgument
from flake8.options import manager

TEST_VERSION = "3.0.0b1"


@pytest.fixture
def optmanager():
    """Generate a simple OptionManager with default test arguments."""
    return manager.OptionManager(
        version=TEST_VERSION,
        plugin_versions="",
        parents=[],
        formatter_names=[],
    )


def test_option_manager_creates_option_parser(optmanager):
    """Verify that a new manager creates a new parser."""
    assert isinstance(optmanager.parser, argparse.ArgumentParser)


def test_option_manager_including_parent_options():
    """Verify parent options are included in the parsed options."""
    # GIVEN
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--parent")

    # WHEN
    optmanager = manager.OptionManager(
        version=TEST_VERSION,
        plugin_versions="",
        parents=[parent_parser],
        formatter_names=[],
    )
    options = optmanager.parse_args(["--parent", "foo"])

    # THEN
    assert options.parent == "foo"


def test_parse_args_forwarding_default_values(optmanager):
    """Verify default provided values are present in the final result."""
    namespace = argparse.Namespace(foo="bar")
    options = optmanager.parse_args([], namespace)
    assert options.foo == "bar"


def test_parse_args_forwarding_type_coercion(optmanager):
    """Verify default provided values are type converted from add_option."""
    optmanager.add_option("--foo", type=int)
    namespace = argparse.Namespace(foo="5")
    options = optmanager.parse_args([], namespace)
    assert options.foo == 5


def test_add_option_short_option_only(optmanager):
    """Verify the behaviour of adding a short-option only."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option("-s", help="Test short opt")
    assert optmanager.options[0].short_option_name == "-s"


def test_add_option_long_option_only(optmanager):
    """Verify the behaviour of adding a long-option only."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option("--long", help="Test long opt")
    assert optmanager.options[0].short_option_name is manager._ARG.NO
    assert optmanager.options[0].long_option_name == "--long"


def test_add_short_and_long_option_names(optmanager):
    """Verify the behaviour of using both short and long option names."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option("-b", "--both", help="Test both opts")
    assert optmanager.options[0].short_option_name == "-b"
    assert optmanager.options[0].long_option_name == "--both"


def test_add_option_with_custom_args(optmanager):
    """Verify that add_option handles custom Flake8 parameters."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option("--parse", parse_from_config=True)
    optmanager.add_option("--commas", comma_separated_list=True)
    optmanager.add_option("--files", normalize_paths=True)

    attrs = ["parse_from_config", "comma_separated_list", "normalize_paths"]
    for option, attr in zip(optmanager.options, attrs):
        assert getattr(option, attr) is True


def test_parse_args_normalize_path(optmanager):
    """Show that parse_args handles path normalization."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option("--config", normalize_paths=True)

    options = optmanager.parse_args(["--config", "../config.ini"])
    assert options.config == os.path.abspath("../config.ini")


def test_parse_args_handles_comma_separated_defaults(optmanager):
    """Show that parse_args handles defaults that are comma-separated."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option(
        "--exclude", default="E123,W234", comma_separated_list=True
    )

    options = optmanager.parse_args([])
    assert options.exclude == ["E123", "W234"]


def test_parse_args_handles_comma_separated_lists(optmanager):
    """Show that parse_args handles user-specified comma-separated lists."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option(
        "--exclude", default="E123,W234", comma_separated_list=True
    )

    options = optmanager.parse_args(["--exclude", "E201,W111,F280"])
    assert options.exclude == ["E201", "W111", "F280"]


def test_parse_args_normalize_paths(optmanager):
    """Verify parse_args normalizes a comma-separated list of paths."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option(
        "--extra-config", normalize_paths=True, comma_separated_list=True
    )

    options = optmanager.parse_args(
        ["--extra-config", "../config.ini,tox.ini,flake8/some-other.cfg"]
    )
    assert options.extra_config == [
        os.path.abspath("../config.ini"),
        "tox.ini",
        os.path.abspath("flake8/some-other.cfg"),
    ]


def test_extend_default_ignore(optmanager):
    """Verify that we update the extended default ignore list."""
    assert optmanager.extended_default_ignore == []

    optmanager.extend_default_ignore(["T100", "T101", "T102"])
    assert optmanager.extended_default_ignore == ["T100", "T101", "T102"]


@pytest.mark.parametrize(
    ("s", "is_auto", "n_jobs"),
    (
        ("auto", True, -1),
        ("4", False, 4),
    ),
)
def test_parse_valid_jobs_argument(s, is_auto, n_jobs):
    """Test that --jobs properly parses valid arguments."""
    jobs_opt = JobsArgument(s)
    assert is_auto == jobs_opt.is_auto
    assert n_jobs == jobs_opt.n_jobs


def test_parse_invalid_jobs_argument(optmanager, capsys):
    """Test that --jobs properly rejects invalid arguments."""
    namespace = argparse.Namespace()
    optmanager.add_option("--jobs", type=JobsArgument)
    with pytest.raises(SystemExit):
        optmanager.parse_args(["--jobs=foo"], namespace)
    out, err = capsys.readouterr()
    output = out + err
    expected = (
        "\nflake8: error: argument --jobs: "
        "'foo' must be 'auto' or an integer.\n"
    )
    assert expected in output


def test_jobs_argument_str():
    """Test that JobsArgument has a correct __str__."""
    assert str(JobsArgument("auto")) == "auto"
    assert str(JobsArgument("123")) == "123"


def test_jobs_argument_repr():
    """Test that JobsArgument has a correct __repr__."""
    assert repr(JobsArgument("auto")) == "JobsArgument('auto')"
    assert repr(JobsArgument("123")) == "JobsArgument('123')"
