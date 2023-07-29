"""Tests for the FileProcessor class."""
from __future__ import annotations

import ast
import tokenize
from unittest import mock

import pytest

from flake8 import processor


def test_read_lines_splits_lines(default_options):
    """Verify that read_lines splits the lines of the file."""
    file_processor = processor.FileProcessor(__file__, default_options)
    lines = file_processor.lines
    assert len(lines) > 5
    assert lines[0].strip() == '"""Tests for the FileProcessor class."""'


def _lines_from_file(tmpdir, contents, options):
    f = tmpdir.join("f.py")
    # be careful to write the bytes exactly to avoid newline munging
    f.write_binary(contents)
    return processor.FileProcessor(f.strpath, options).lines


def test_read_lines_universal_newlines(tmpdir, default_options):
    r"""Verify that line endings are translated to \n."""
    lines = _lines_from_file(
        tmpdir, b"# coding: utf-8\r\nx = 1\r\n", default_options
    )
    assert lines == ["# coding: utf-8\n", "x = 1\n"]


def test_read_lines_incorrect_utf_16(tmpdir, default_options):
    """Verify that an incorrectly encoded file is read as latin-1."""
    lines = _lines_from_file(
        tmpdir, b"# coding: utf16\nx = 1\n", default_options
    )
    assert lines == ["# coding: utf16\n", "x = 1\n"]


def test_read_lines_unknown_encoding(tmpdir, default_options):
    """Verify that an unknown encoding is still read as latin-1."""
    lines = _lines_from_file(
        tmpdir, b"# coding: fake-encoding\nx = 1\n", default_options
    )
    assert lines == ["# coding: fake-encoding\n", "x = 1\n"]


@pytest.mark.parametrize(
    "first_line",
    [
        '\xEF\xBB\xBF"""Module docstring."""\n',
        '\uFEFF"""Module docstring."""\n',
    ],
)
def test_strip_utf_bom(first_line, default_options):
    r"""Verify that we strip '\xEF\xBB\xBF' from the first line."""
    lines = [first_line]
    file_processor = processor.FileProcessor("-", default_options, lines[:])
    assert file_processor.lines != lines
    assert file_processor.lines[0] == '"""Module docstring."""\n'


@pytest.mark.parametrize(
    "lines, expected",
    [
        (['\xEF\xBB\xBF"""Module docstring."""\n'], False),
        (['\uFEFF"""Module docstring."""\n'], False),
        (["#!/usr/bin/python", "# flake8 is great", "a = 1"], False),
        (["#!/usr/bin/python", "# flake8: noqa", "a = 1"], True),
        (["#!/usr/bin/python", "# flake8:noqa", "a = 1"], True),
        (["# flake8: noqa", "#!/usr/bin/python", "a = 1"], True),
        (["# flake8:noqa", "#!/usr/bin/python", "a = 1"], True),
        (["#!/usr/bin/python", "a = 1", "# flake8: noqa"], True),
        (["#!/usr/bin/python", "a = 1", "# flake8:noqa"], True),
        (["#!/usr/bin/python", "a = 1  # flake8: noqa"], False),
        (["#!/usr/bin/python", "a = 1  # flake8:noqa"], False),
    ],
)
def test_should_ignore_file(lines, expected, default_options):
    """Verify that we ignore a file if told to."""
    file_processor = processor.FileProcessor("-", default_options, lines)
    assert file_processor.should_ignore_file() is expected


def test_should_ignore_file_to_handle_disable_noqa(default_options):
    """Verify that we ignore a file if told to."""
    lines = ["# flake8: noqa"]
    file_processor = processor.FileProcessor("-", default_options, lines)
    assert file_processor.should_ignore_file() is True
    default_options.disable_noqa = True
    file_processor = processor.FileProcessor("-", default_options, lines)
    assert file_processor.should_ignore_file() is False


@mock.patch("flake8.utils.stdin_get_value")
def test_read_lines_from_stdin(stdin_get_value, default_options):
    """Verify that we use our own utility function to retrieve stdin."""
    stdin_get_value.return_value = ""
    processor.FileProcessor("-", default_options)
    stdin_get_value.assert_called_once_with()


@mock.patch("flake8.utils.stdin_get_value")
def test_stdin_filename_attribute(stdin_get_value, default_options):
    """Verify that we update the filename attribute."""
    stdin_get_value.return_value = ""
    file_processor = processor.FileProcessor("-", default_options)
    assert file_processor.filename == "stdin"


@mock.patch("flake8.utils.stdin_get_value")
def test_read_lines_uses_display_name(stdin_get_value, default_options):
    """Verify that when processing stdin we use a display name if present."""
    default_options.stdin_display_name = "display_name.py"
    stdin_get_value.return_value = ""
    file_processor = processor.FileProcessor("-", default_options)
    assert file_processor.filename == "display_name.py"


@mock.patch("flake8.utils.stdin_get_value")
def test_read_lines_ignores_empty_display_name(
    stdin_get_value,
    default_options,
):
    """Verify that when processing stdin we use a display name if present."""
    stdin_get_value.return_value = ""
    default_options.stdin_display_name = ""
    file_processor = processor.FileProcessor("-", default_options)
    assert file_processor.filename == "stdin"


def test_noqa_line_for(default_options):
    """Verify we grab the correct line from the cached lines."""
    file_processor = processor.FileProcessor(
        "-",
        default_options,
        lines=[
            "Line 1\n",
            "Line 2\n",
            "Line 3\n",
        ],
    )

    for i in range(1, 4):
        assert file_processor.noqa_line_for(i) == f"Line {i}\n"


def test_noqa_line_for_continuation(default_options):
    """Verify that the correct "line" is retrieved for continuation."""
    src = '''\
from foo \\
    import bar  # 2

x = """
hello
world
"""  # 7
'''
    lines = src.splitlines(True)
    file_processor = processor.FileProcessor("-", default_options, lines=lines)

    assert file_processor.noqa_line_for(0) is None

    l_1_2 = "from foo \\\n    import bar  # 2\n"
    assert file_processor.noqa_line_for(1) == l_1_2
    assert file_processor.noqa_line_for(2) == l_1_2

    assert file_processor.noqa_line_for(3) == "\n"

    l_4_7 = 'x = """\nhello\nworld\n"""  # 7\n'
    for i in (4, 5, 6, 7):
        assert file_processor.noqa_line_for(i) == l_4_7

    assert file_processor.noqa_line_for(8) is None


def test_noqa_line_for_no_eol_at_end_of_file(default_options):
    """Verify that we properly handle noqa line at the end of the file."""
    src = "from foo \\\nimport bar"  # no end of file newline
    lines = src.splitlines(True)
    file_processor = processor.FileProcessor("-", default_options, lines=lines)

    l_1_2 = "from foo \\\nimport bar"
    assert file_processor.noqa_line_for(1) == l_1_2
    assert file_processor.noqa_line_for(2) == l_1_2


def test_next_line(default_options):
    """Verify we update the file_processor state for each new line."""
    file_processor = processor.FileProcessor(
        "-",
        default_options,
        lines=[
            "Line 1",
            "Line 2",
            "Line 3",
        ],
    )

    for i in range(1, 4):
        assert file_processor.next_line() == f"Line {i}"
        assert file_processor.line_number == i


@pytest.mark.parametrize(
    "params, args, expected_kwargs",
    [
        (
            {"blank_before": True, "blank_lines": True},
            {},
            {"blank_before": 0, "blank_lines": 0},
        ),
        (
            {"noqa": True, "fake": True},
            {"fake": "foo"},
            {"noqa": False},
        ),
        (
            {"blank_before": True, "blank_lines": True, "noqa": True},
            {"blank_before": 10, "blank_lines": 5, "noqa": True},
            {},
        ),
        ({}, {"fake": "foo"}, {}),
        ({"non-existent": False}, {"fake": "foo"}, {}),
    ],
)
def test_keyword_arguments_for(params, args, expected_kwargs, default_options):
    """Verify the keyword args are generated properly."""
    file_processor = processor.FileProcessor(
        "-",
        default_options,
        lines=[
            "Line 1",
        ],
    )
    ret = file_processor.keyword_arguments_for(params, args)

    assert ret == expected_kwargs


def test_keyword_arguments_for_does_not_handle_attribute_errors(
    default_options,
):
    """Verify we re-raise AttributeErrors."""
    file_processor = processor.FileProcessor(
        "-",
        default_options,
        lines=[
            "Line 1",
        ],
    )

    with pytest.raises(AttributeError):
        file_processor.keyword_arguments_for({"fake": True}, {})


def test_processor_split_line(default_options):
    file_processor = processor.FileProcessor(
        "-",
        default_options,
        lines=[
            'x = """\n',
            "contents\n",
            '"""\n',
        ],
    )
    token = tokenize.TokenInfo(
        3,
        '"""\ncontents\n"""',
        (1, 4),
        (3, 3),
        'x = """\ncontents\n"""\n',
    )
    expected = [('x = """\n', 1, True), ("contents\n", 2, True)]
    assert file_processor.multiline is False
    actual = [
        (line, file_processor.line_number, file_processor.multiline)
        for line in file_processor.multiline_string(token)
    ]
    assert file_processor.multiline is False
    assert expected == actual
    assert file_processor.line_number == 3


def test_build_ast(default_options):
    """Verify the logic for how we build an AST for plugins."""
    file_processor = processor.FileProcessor(
        "-", default_options, lines=["a = 1\n"]
    )

    module = file_processor.build_ast()
    assert isinstance(module, ast.Module)


def test_next_logical_line_updates_the_previous_logical_line(default_options):
    """Verify that we update our tracking of the previous logical line."""
    file_processor = processor.FileProcessor(
        "-", default_options, lines=["a = 1\n"]
    )

    file_processor.indent_level = 1
    file_processor.logical_line = "a = 1"
    assert file_processor.previous_logical == ""
    assert file_processor.previous_indent_level == 0

    file_processor.next_logical_line()
    assert file_processor.previous_logical == "a = 1"
    assert file_processor.previous_indent_level == 1


def test_visited_new_blank_line(default_options):
    """Verify we update the number of blank lines seen."""
    file_processor = processor.FileProcessor(
        "-", default_options, lines=["a = 1\n"]
    )

    assert file_processor.blank_lines == 0
    file_processor.visited_new_blank_line()
    assert file_processor.blank_lines == 1


@pytest.mark.parametrize(
    "string, expected",
    [
        ('""', '""'),
        ("''", "''"),
        ('"a"', '"x"'),
        ("'a'", "'x'"),
        ('"x"', '"x"'),
        ("'x'", "'x'"),
        ('"abcdef"', '"xxxxxx"'),
        ("'abcdef'", "'xxxxxx'"),
        ('""""""', '""""""'),
        ("''''''", "''''''"),
        ('"""a"""', '"""x"""'),
        ("'''a'''", "'''x'''"),
        ('"""x"""', '"""x"""'),
        ("'''x'''", "'''x'''"),
        ('"""abcdef"""', '"""xxxxxx"""'),
        ("'''abcdef'''", "'''xxxxxx'''"),
        ('"""xxxxxx"""', '"""xxxxxx"""'),
        ("'''xxxxxx'''", "'''xxxxxx'''"),
    ],
)
def test_mutate_string(string, expected, default_options):
    """Verify we appropriately mutate the string to sanitize it."""
    actual = processor.mutate_string(string)
    assert expected == actual


@pytest.mark.parametrize(
    "string, expected",
    [
        ("    ", 4),
        ("      ", 6),
        ("\t", 8),
        ("\t\t", 16),
        ("       \t", 8),
        ("        \t", 16),
    ],
)
def test_expand_indent(string, expected):
    """Verify we correctly measure the amount of indentation."""
    actual = processor.expand_indent(string)
    assert expected == actual


@pytest.mark.parametrize(
    "current_count, token_text, expected",
    [
        (0, "(", 1),
        (0, "[", 1),
        (0, "{", 1),
        (1, ")", 0),
        (1, "]", 0),
        (1, "}", 0),
        (10, "+", 10),
    ],
)
def test_count_parentheses(current_count, token_text, expected):
    """Verify our arithmetic is correct."""
    assert processor.count_parentheses(current_count, token_text) == expected


def test_nonexistent_file(default_options):
    """Verify that FileProcessor raises IOError when a file does not exist."""
    with pytest.raises(IOError):
        processor.FileProcessor("foobar.py", default_options)
