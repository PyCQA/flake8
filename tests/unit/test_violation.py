"""Tests for the flake8.violation.Violation class."""
from __future__ import annotations

from unittest import mock

import pytest

from flake8.violation import Violation


@pytest.mark.parametrize(
    "error_code,physical_line,expected_result",
    [
        ("E111", "a = 1", False),
        ("E121", "a = 1  # noqa: E111", False),
        ("E121", "a = 1  # noqa: E111,W123,F821", False),
        ("E111", "a = 1  # noqa: E111,W123,F821", True),
        ("W123", "a = 1  # noqa: E111,W123,F821", True),
        ("W123", "a = 1  # noqa: E111, W123,F821", True),
        ("E111", "a = 1  # noqa: E11,W123,F821", True),
        ("E121", "a = 1  # noqa:E111,W123,F821", False),
        ("E111", "a = 1  # noqa:E111,W123,F821", True),
        ("W123", "a = 1  # noqa:E111,W123,F821", True),
        ("W123", "a = 1  # noqa:E111, W123,F821", True),
        ("E111", "a = 1  # noqa:E11,W123,F821", True),
        ("E111", "a = 1  # noqa, analysis:ignore", True),
        ("E111", "a = 1  # noqa analysis:ignore", True),
        ("E111", "a = 1  # noqa - We do not care", True),
        ("E111", "a = 1  # noqa: We do not care", True),
        ("E111", "a = 1  # noqa:We do not care", True),
        ("ABC123", "a = 1  # noqa: ABC123", True),
        ("E111", "a = 1  # noqa: ABC123", False),
        ("ABC123", "a = 1  # noqa: ABC124", False),
    ],
)
def test_is_inline_ignored(error_code, physical_line, expected_result):
    """Verify that we detect inline usage of ``# noqa``."""
    error = Violation(error_code, "filename.py", 1, 1, "error text", None)
    # We want `None` to be passed as the physical line so we actually use our
    # monkey-patched linecache.getline value.

    with mock.patch("linecache.getline", return_value=physical_line):
        assert error.is_inline_ignored(False) is expected_result


def test_disable_is_inline_ignored():
    """Verify that is_inline_ignored exits immediately if disabling NoQA."""
    error = Violation("E121", "filename.py", 1, 1, "error text", "line")

    with mock.patch("linecache.getline") as getline:
        assert error.is_inline_ignored(True) is False

    assert getline.called is False


def _bi_tc(error_code, physical_line, block_start, filename, expected_result):
    if block_start is None:
        physical_lines = [physical_line]
        line_no = 1
    else:
        block_end = "# noqa: off"
        physical_lines = [block_start, physical_line, block_end]
        line_no = 2

    return (error_code, filename, physical_lines, line_no, expected_result)


@pytest.mark.parametrize(
    "error_code,filename,physical_lines,line_no,expected_result",
    [
        _bi_tc("E111", "a = 1", None, "filename-1.py", False),
        _bi_tc("E121", "a = 1", "# noqa: on E111", "filename-2.py", False),
        _bi_tc(
            "E121",
            "a = 1",
            "# noqa: on E111,W123,F821",
            "filename-3.py",
            False,
        ),
        _bi_tc(
            "E111", "a = 1", "# noqa: on E111,W123,F821", "filename-4.py", True
        ),
        _bi_tc(
            "W123", "a = 1", "# noqa: on E111,W123,F821", "filename-5.py", True
        ),
        _bi_tc(
            "W123",
            "a = 1",
            "# noqa: on E111, W123,F821",
            "filename-6.py",
            True,
        ),
        _bi_tc(
            "E111", "a = 1", "# noqa: on E11,W123,F821", "filename-7.py", True
        ),
        _bi_tc(
            "E121", "a = 1", "# noqa:on E111,W123,F821", "filename-8.py", False
        ),
        _bi_tc(
            "E111", "a = 1", "# noqa:on E111,W123,F821", "filename-9.py", True
        ),
        _bi_tc(
            "W123", "a = 1", "# noqa:on E111,W123,F821", "filename-10.py", True
        ),
        _bi_tc(
            "W123",
            "a = 1",
            "# noqa:on E111, W123,F821",
            "filename-11.py",
            True,
        ),
        _bi_tc(
            "E111", "a = 1", "# noqa:on E11,W123,F821", "filename-12.py", True
        ),
        _bi_tc(
            "E111",
            "a = 1",
            "# noqa: on - We do not care",
            "filename-13.py",
            True,
        ),
        _bi_tc(
            "E111",
            "a = 1",
            "# noqa: on We do not care",
            "filename-14.py",
            True,
        ),
        _bi_tc(
            "E111", "a = 1", "# noqa:On We do not care", "filename-15.py", True
        ),
        _bi_tc("ABC123", "a = 1", "# noqa: on ABC123", "filename-16.py", True),
        _bi_tc("E111", "a = 1", "# noqa: on ABC123", "filename-17.py", False),
        _bi_tc(
            "ABC123", "a = 1", "# noqa: on ABC124", "filename-18.py", False
        ),
        _bi_tc("ABC123", "a = 1", "# noqa: ABC124", "filename-19.py", False),
        _bi_tc(
            "ABC123", "a = 1", "# noqa: off ABC124", "filename-19.py", False
        ),
    ],
)
def test_is_block_ignored(
    error_code,
    filename,
    physical_lines,
    line_no,
    expected_result,
):
    """Verify that we detect block usage of ``# noqa: off/on``."""
    error = Violation(error_code, filename, line_no, 1, "error text", None)

    with mock.patch("linecache.getlines", return_value=physical_lines):
        assert error.is_block_ignored(False) is expected_result


def test_disable_is_block_ignored():
    """Verify that is_block_ignored exits immediately if disabling NoQA."""
    error = Violation("E121", "filename.py", 1, 1, "error text", "line")

    with mock.patch("linecache.getlines") as getlines:
        assert error.is_block_ignored(True) is False

    assert getlines.called is False
