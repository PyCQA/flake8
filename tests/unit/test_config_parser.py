"""Unit tests for flake8.options.config.ConfigParser."""
import os
from unittest import mock

import pytest

from flake8.options import config
from flake8.options import manager


@pytest.fixture
def optmanager():
    """Generate an OptionManager with simple values."""
    return manager.OptionManager(prog="flake8", version="3.0.0a1")


@pytest.fixture
def config_finder():
    """Generate a simple ConfigFileFinder."""
    return config.ConfigFileFinder("flake8")


def test_parse_cli_config(optmanager, config_finder):
    """Parse the specified config file as a cli config file."""
    optmanager.add_option(
        "--exclude",
        parse_from_config=True,
        comma_separated_list=True,
        normalize_paths=True,
    )
    optmanager.add_option(
        "--ignore", parse_from_config=True, comma_separated_list=True
    )
    optmanager.add_option("--quiet", parse_from_config=True, action="count")
    parser = config.ConfigParser(optmanager, config_finder)

    config_file = "tests/fixtures/config_files/cli-specified.ini"
    parsed_config = parser.parse_cli_config(config_file)

    config_dir = os.path.dirname(config_file)
    assert parsed_config == {
        "ignore": ["E123", "W234", "E111"],
        "exclude": [
            os.path.abspath(os.path.join(config_dir, "foo/")),
            os.path.abspath(os.path.join(config_dir, "bar/")),
            os.path.abspath(os.path.join(config_dir, "bogus/")),
        ],
        "quiet": 1,
    }


@pytest.mark.parametrize(
    "filename,is_configured_by",
    [
        ("tests/fixtures/config_files/cli-specified.ini", True),
        ("tests/fixtures/config_files/no-flake8-section.ini", False),
    ],
)
def test_is_configured_by(
    filename, is_configured_by, optmanager, config_finder
):
    """Verify the behaviour of the is_configured_by method."""
    parsed_config, _ = config.ConfigFileFinder._read_config(filename)
    parser = config.ConfigParser(optmanager, config_finder)

    assert parser.is_configured_by(parsed_config) is is_configured_by


def test_parse_local_config(optmanager, config_finder):
    """Verify parsing of local config files."""
    optmanager.add_option(
        "--exclude",
        parse_from_config=True,
        comma_separated_list=True,
        normalize_paths=True,
    )
    optmanager.add_option(
        "--ignore", parse_from_config=True, comma_separated_list=True
    )
    optmanager.add_option("--quiet", parse_from_config=True, action="count")
    parser = config.ConfigParser(optmanager, config_finder)

    with mock.patch.object(config_finder, "local_config_files") as localcfs:
        localcfs.return_value = [
            "tests/fixtures/config_files/cli-specified.ini"
        ]
        parsed_config = parser.parse_local_config()

    assert parsed_config == {
        "ignore": ["E123", "W234", "E111"],
        "exclude": [
            os.path.abspath("foo/"),
            os.path.abspath("bar/"),
            os.path.abspath("bogus/"),
        ],
        "quiet": 1,
    }


def test_parse_isolates_config(optmanager):
    """Verify behaviour of the parse method with isolated=True."""
    config_finder = mock.MagicMock()
    config_finder.ignore_config_files = True
    parser = config.ConfigParser(optmanager, config_finder)

    assert parser.parse() == {}
    assert config_finder.local_configs.called is False


def test_parse_uses_cli_config(optmanager):
    """Verify behaviour of the parse method with a specified config."""
    config_file_value = "foo.ini"
    config_finder = mock.MagicMock()
    config_finder.config_file = config_file_value
    config_finder.ignore_config_files = False
    parser = config.ConfigParser(optmanager, config_finder)

    parser.parse()
    config_finder.cli_config.assert_called_once_with(config_file_value)


@pytest.mark.parametrize(
    "config_fixture_path",
    [
        "tests/fixtures/config_files/cli-specified.ini",
        "tests/fixtures/config_files/cli-specified-with-inline-comments.ini",
        "tests/fixtures/config_files/cli-specified-without-inline-comments.ini",  # noqa: E501
    ],
)
def test_parsed_configs_are_equivalent(
    optmanager, config_finder, config_fixture_path
):
    """Verify the each file matches the expected parsed output.

    This is used to ensure our documented behaviour does not regress.
    """
    optmanager.add_option(
        "--exclude",
        parse_from_config=True,
        comma_separated_list=True,
        normalize_paths=True,
    )
    optmanager.add_option(
        "--ignore", parse_from_config=True, comma_separated_list=True
    )
    parser = config.ConfigParser(optmanager, config_finder)

    with mock.patch.object(config_finder, "local_config_files") as localcfs:
        localcfs.return_value = [config_fixture_path]
        parsed_config = parser.parse()

    assert parsed_config["ignore"] == ["E123", "W234", "E111"]
    assert parsed_config["exclude"] == [
        os.path.abspath("foo/"),
        os.path.abspath("bar/"),
        os.path.abspath("bogus/"),
    ]


@pytest.mark.parametrize(
    "config_file",
    ["tests/fixtures/config_files/config-with-hyphenated-options.ini"],
)
def test_parsed_hyphenated_and_underscored_names(
    optmanager, config_finder, config_file
):
    """Verify we find hyphenated option names as well as underscored.

    This tests for options like --max-line-length and --enable-extensions
    which are able to be specified either as max-line-length or
    max_line_length in our config files.
    """
    optmanager.add_option(
        "--max-line-length", parse_from_config=True, type=int
    )
    optmanager.add_option(
        "--enable-extensions",
        parse_from_config=True,
        comma_separated_list=True,
    )
    parser = config.ConfigParser(optmanager, config_finder)

    with mock.patch.object(config_finder, "local_config_files") as localcfs:
        localcfs.return_value = [config_file]
        parsed_config = parser.parse()

    assert parsed_config["max_line_length"] == 110
    assert parsed_config["enable_extensions"] == ["H101", "H235"]
