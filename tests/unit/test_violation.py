"""Tests for the flake8.violation.Violation class."""
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


@pytest.mark.parametrize(
    "violation_file,violation_line,diff,expected",
    [
        ("file.py", 10, {}, True),
        ("file.py", 1, {"file.py": range(1, 2)}, True),
        ("file.py", 10, {"file.py": range(1, 2)}, False),
        ("file.py", 1, {"other.py": range(1, 2)}, False),
        ("file.py", 10, {"other.py": range(1, 2)}, False),
    ],
)
def test_violation_is_in_diff(violation_file, violation_line, diff, expected):
    """Verify that we find violations within a diff."""
    violation = Violation(
        "E001", violation_file, violation_line, 1, "warning", "line"
    )

    assert violation.is_in(diff) is expected
