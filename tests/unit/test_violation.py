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
