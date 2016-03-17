"""Tests for the FileProcessor class."""
import optparse

from flake8 import processor

import pytest


def options_from(**kwargs):
    """Generate a Values instances with our kwargs."""
    kwargs.setdefault('hang_closing', True)
    kwargs.setdefault('max_line_length', 79)
    kwargs.setdefault('verbose', False)
    return optparse.Values(kwargs)


def test_read_lines_splits_lines():
    """Verify that read_lines splits the lines of the file."""
    file_processor = processor.FileProcessor(__file__, options_from())
    lines = file_processor.lines
    assert len(lines) > 5
    assert '"""Tests for the FileProcessor class."""\n' in lines


@pytest.mark.parametrize('first_line', [
    '\xEF\xBB\xBF"""Module docstring."""\n',
    u'\uFEFF"""Module docstring."""\n',
])
def test_strip_utf_bom(first_line):
    r"""Verify that we strip '\xEF\xBB\xBF' from the first line."""
    lines = [first_line]
    file_processor = processor.FileProcessor('-', options_from(), lines[:])
    assert file_processor.lines != lines
    assert file_processor.lines[0] == '"""Module docstring."""\n'


@pytest.mark.parametrize('lines, expected', [
    (['\xEF\xBB\xBF"""Module docstring."""\n'], False),
    ([u'\uFEFF"""Module docstring."""\n'], False),
    (['#!/usr/bin/python', '# flake8 is great', 'a = 1'], False),
    (['#!/usr/bin/python', '# flake8: noqa', 'a = 1'], True),
    (['# flake8: noqa', '#!/usr/bin/python', 'a = 1'], True),
    (['#!/usr/bin/python', 'a = 1', '# flake8: noqa'], True),
])
def test_should_ignore_file(lines, expected):
    """Verify that we ignore a file if told to."""
    file_processor = processor.FileProcessor('-', options_from(), lines)
    assert file_processor.should_ignore_file() is expected
