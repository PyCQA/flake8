"""Tests for the FileChecker class."""
from flake8 import checker

import pytest


def test_read_lines_splits_lines():
    """Verify that read_lines splits the lines of the file."""
    file_checker = checker.FileChecker(__file__, [])
    lines = file_checker.read_lines()
    assert len(lines) > 5
    assert '"""Tests for the FileChecker class."""\n' in lines


@pytest.mark.parametrize('first_line', [
    '\xEF\xBB\xBF"""Module docstring."""\n',
    '\uFEFF"""Module docstring."""\n',
])
def test_strip_utf_bom(first_line):
    r"""Verify that we strip '\xEF\xBB\xBF' from the first line."""
    lines = [first_line]
    file_checker = checker.FileChecker('stdin', [])
    file_checker.lines = lines[:]
    file_checker.strip_utf_bom()
    assert file_checker.lines != lines
    assert file_checker.lines[0] == '"""Module docstring."""\n'
