"""Tests for flake8's utils module."""
import io
import logging
import os
import sys
from unittest import mock

import pytest

from flake8 import exceptions
from flake8 import utils

RELATIVE_PATHS = ["flake8", "pep8", "pyflakes", "mccabe"]


@pytest.mark.parametrize(
    "value,expected",
    [
        ("E123,\n\tW234,\n    E206", ["E123", "W234", "E206"]),
        ("E123,W234,E206", ["E123", "W234", "E206"]),
        ("E123 W234 E206", ["E123", "W234", "E206"]),
        ("E123\nW234 E206", ["E123", "W234", "E206"]),
        ("E123\nW234\nE206", ["E123", "W234", "E206"]),
        ("E123,W234,E206,", ["E123", "W234", "E206"]),
        ("E123,W234,E206, ,\n", ["E123", "W234", "E206"]),
        ("E123,W234,,E206,,", ["E123", "W234", "E206"]),
        ("E123, W234,, E206,,", ["E123", "W234", "E206"]),
        ("E123,,W234,,E206,,", ["E123", "W234", "E206"]),
        ("", []),
    ],
)
def test_parse_comma_separated_list(value, expected):
    """Verify that similar inputs produce identical outputs."""
    assert utils.parse_comma_separated_list(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        # empty option configures nothing
        ("", []),
        ("   ", []),
        ("\n\n\n", []),
        # basic case
        (
            "f.py:E123",
            [("f.py", ["E123"])],
        ),
        # multiple filenames, multiple codes
        (
            "f.py,g.py:E,F",
            [("f.py", ["E", "F"]), ("g.py", ["E", "F"])],
        ),
        # demonstrate that whitespace is not important around tokens
        (
            "   f.py  , g.py  : E  , F  ",
            [("f.py", ["E", "F"]), ("g.py", ["E", "F"])],
        ),
        # whitespace can separate groups of configuration
        (
            "f.py:E g.py:F",
            [("f.py", ["E"]), ("g.py", ["F"])],
        ),
        # newlines can separate groups of configuration
        (
            "f.py: E\ng.py: F\n",
            [("f.py", ["E"]), ("g.py", ["F"])],
        ),
        # whitespace can be used in place of commas
        (
            "f.py g.py: E F",
            [("f.py", ["E", "F"]), ("g.py", ["E", "F"])],
        ),
        # go ahead, indent your codes
        (
            "f.py:\n    E,F\ng.py:\n    G,H",
            [("f.py", ["E", "F"]), ("g.py", ["G", "H"])],
        ),
        # capitalized filenames are ok too
        (
            "F.py,G.py: F,G",
            [("F.py", ["F", "G"]), ("G.py", ["F", "G"])],
        ),
        #  it's easier to allow zero filenames or zero codes than forbid it
        (":E", []),
        ("f.py:", []),
        (":E f.py:F", [("f.py", ["F"])]),
        ("f.py: g.py:F", [("g.py", ["F"])]),
        ("f.py:E:", []),
        ("f.py:E.py:", []),
        ("f.py:Eg.py:F", [("Eg.py", ["F"])]),
        # sequences are also valid (?)
        (
            ["f.py:E,F", "g.py:G,H"],
            [("f.py", ["E", "F"]), ("g.py", ["G", "H"])],
        ),
        # six-digits codes are allowed
        (
            "f.py: ABC123",
            [("f.py", ["ABC123"])],
        ),
    ),
)
def test_parse_files_to_codes_mapping(value, expected):
    """Test parsing of valid files-to-codes mappings."""
    assert utils.parse_files_to_codes_mapping(value) == expected


@pytest.mark.parametrize(
    "value",
    (
        # code while looking for filenames
        "E123",
        "f.py,E123",
        "f.py E123",
        # eof while looking for filenames
        "f.py",
        "f.py:E,g.py"
        # colon while looking for codes
        "f.py::",
        # no separator between
        "f.py:E1F1",
    ),
)
def test_invalid_file_list(value):
    """Test parsing of invalid files-to-codes mappings."""
    with pytest.raises(exceptions.ExecutionError):
        utils.parse_files_to_codes_mapping(value)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("flake8", "flake8"),
        (".", os.path.abspath(".")),
        ("../flake8", os.path.abspath("../flake8")),
        ("flake8/", os.path.abspath("flake8")),
    ],
)
def test_normalize_path(value, expected):
    """Verify that we normalize paths provided to the tool."""
    assert utils.normalize_path(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            ["flake8", "pep8", "pyflakes", "mccabe"],
            ["flake8", "pep8", "pyflakes", "mccabe"],
        ),
        (
            ["../flake8", "../pep8", "../pyflakes", "../mccabe"],
            [os.path.abspath(f"../{p}") for p in RELATIVE_PATHS],
        ),
    ],
)
def test_normalize_paths(value, expected):
    """Verify we normalizes a sequence of paths provided to the tool."""
    assert utils.normalize_paths(value) == expected


def test_matches_filename_for_excluding_dotfiles():
    """Verify that `.` and `..` are not matched by `.*`."""
    logger = logging.Logger(__name__)
    assert not utils.matches_filename(".", (".*",), "", logger)
    assert not utils.matches_filename("..", (".*",), "", logger)


@pytest.mark.parametrize(
    "filename,patterns,expected",
    [
        ("foo.py", [], True),
        ("foo.py", ["*.pyc"], False),
        ("foo.pyc", ["*.pyc"], True),
        ("foo.pyc", ["*.swp", "*.pyc", "*.py"], True),
    ],
)
def test_fnmatch(filename, patterns, expected):
    """Verify that our fnmatch wrapper works as expected."""
    assert utils.fnmatch(filename, patterns) is expected


def read_diff_file(filename):
    """Read the diff file in its entirety."""
    with open(filename) as fd:
        content = fd.read()
    return content


SINGLE_FILE_DIFF = read_diff_file("tests/fixtures/diffs/single_file_diff")
SINGLE_FILE_INFO = {
    "flake8/utils.py": set(range(75, 83)).union(set(range(84, 94))),
}
TWO_FILE_DIFF = read_diff_file("tests/fixtures/diffs/two_file_diff")
TWO_FILE_INFO = {
    "flake8/utils.py": set(range(75, 83)).union(set(range(84, 94))),
    "tests/unit/test_utils.py": set(range(115, 128)),
}
MULTI_FILE_DIFF = read_diff_file("tests/fixtures/diffs/multi_file_diff")
MULTI_FILE_INFO = {
    "flake8/utils.py": set(range(75, 83)).union(set(range(84, 94))),
    "tests/unit/test_utils.py": set(range(115, 129)),
    "tests/fixtures/diffs/single_file_diff": set(range(1, 28)),
    "tests/fixtures/diffs/two_file_diff": set(range(1, 46)),
}


@pytest.mark.parametrize(
    "diff, parsed_diff",
    [
        (SINGLE_FILE_DIFF, SINGLE_FILE_INFO),
        (TWO_FILE_DIFF, TWO_FILE_INFO),
        (MULTI_FILE_DIFF, MULTI_FILE_INFO),
    ],
)
def test_parse_unified_diff(diff, parsed_diff):
    """Verify that what we parse from a diff matches expectations."""
    assert utils.parse_unified_diff(diff) == parsed_diff


def test_stdin_get_value_crlf():
    """Ensure that stdin is normalized from crlf to lf."""
    stdin = io.TextIOWrapper(io.BytesIO(b"1\r\n2\r\n"), "UTF-8")
    with mock.patch.object(sys, "stdin", stdin):
        assert utils.stdin_get_value.__wrapped__() == "1\n2\n"


def test_stdin_unknown_coding_token():
    """Ensure we produce source even for unknown encodings."""
    stdin = io.TextIOWrapper(io.BytesIO(b"# coding: unknown\n"), "UTF-8")
    with mock.patch.object(sys, "stdin", stdin):
        assert utils.stdin_get_value.__wrapped__() == "# coding: unknown\n"


@pytest.mark.parametrize(
    ("s", "expected"),
    (
        ("", ""),
        ("my-plugin", "my-plugin"),
        ("MyPlugin", "myplugin"),
        ("my_plugin", "my-plugin"),
        ("my.plugin", "my-plugin"),
        ("my--plugin", "my-plugin"),
        ("my__plugin", "my-plugin"),
    ),
)
def test_normalize_pypi_name(s, expected):
    assert utils.normalize_pypi_name(s) == expected
