"""Tests for the BaseFormatter object."""
from __future__ import annotations

import argparse
import sys
from unittest import mock

import pytest

from flake8.formatting import _windows_color
from flake8.formatting import base
from flake8.violation import Violation


def options(**kwargs):
    """Create an argparse.Namespace instance."""
    kwargs.setdefault("color", "auto")
    kwargs.setdefault("output_file", None)
    kwargs.setdefault("tee", False)
    return argparse.Namespace(**kwargs)


@pytest.mark.parametrize("filename", [None, "out.txt"])
def test_start(filename):
    """Verify we open a new file in the start method."""
    mock_open = mock.mock_open()
    formatter = base.BaseFormatter(options(output_file=filename))
    with mock.patch("flake8.formatting.base.open", mock_open):
        formatter.start()

    if filename is None:
        assert mock_open.called is False
    else:
        mock_open.assert_called_once_with(filename, "a")


def test_stop():
    """Verify we close open file objects."""
    filemock = mock.Mock()
    formatter = base.BaseFormatter(options())
    formatter.output_fd = filemock
    formatter.stop()

    filemock.close.assert_called_once_with()
    assert formatter.output_fd is None


def test_format_needs_to_be_implemented():
    """Ensure BaseFormatter#format raises a NotImplementedError."""
    formatter = base.BaseFormatter(options())
    with pytest.raises(NotImplementedError):
        formatter.format(
            Violation("A000", "file.py", 1, 1, "error text", None)
        )


def test_show_source_returns_nothing_when_not_showing_source():
    """Ensure we return nothing when users want nothing."""
    formatter = base.BaseFormatter(options(show_source=False))
    assert (
        formatter.show_source(
            Violation("A000", "file.py", 1, 1, "error text", "line")
        )
        == ""
    )


def test_show_source_returns_nothing_when_there_is_source():
    """Ensure we return nothing when there is no line."""
    formatter = base.BaseFormatter(options(show_source=True))
    assert (
        formatter.show_source(
            Violation("A000", "file.py", 1, 1, "error text", None)
        )
        == ""
    )


@pytest.mark.parametrize(
    ("line1", "line2", "column"),
    [
        (
            "x=1\n",
            " ^",
            2,
        ),
        (
            "    x=(1\n       +2)\n",
            "    ^",
            5,
        ),
        (
            "\tx\t=\ty\n",
            "\t \t \t^",
            6,
        ),
    ],
)
def test_show_source_updates_physical_line_appropriately(line1, line2, column):
    """Ensure the error column is appropriately indicated."""
    formatter = base.BaseFormatter(options(show_source=True))
    error = Violation("A000", "file.py", 1, column, "error", line1)
    output = formatter.show_source(error)
    assert output == line1 + line2


@pytest.mark.parametrize("tee", [False, True])
def test_write_uses_an_output_file(tee, capsys):
    """Verify that we use the output file when it's present."""
    line = "Something to write"
    source = "source"
    filemock = mock.Mock()

    formatter = base.BaseFormatter(options(tee=tee))
    formatter.output_fd = filemock

    formatter.write(line, source)
    if tee:
        assert capsys.readouterr().out == f"{line}\n{source}\n"
    else:
        assert capsys.readouterr().out == ""

    assert filemock.write.called is True
    assert filemock.write.call_count == 2
    assert filemock.write.mock_calls == [
        mock.call(line + formatter.newline),
        mock.call(source + formatter.newline),
    ]


def test_write_produces_stdout(capsys):
    """Verify that we write to stdout without an output file."""
    line = "Something to write"
    source = "source"

    formatter = base.BaseFormatter(options())
    formatter.write(line, source)

    assert capsys.readouterr().out == f"{line}\n{source}\n"


def test_color_always_is_true():
    """Verify that color='always' sets it to True."""
    formatter = base.BaseFormatter(options(color="always"))
    assert formatter.color is True


def _mock_isatty(val):
    attrs = {"isatty.return_value": val}
    return mock.patch.object(sys, "stdout", **attrs)


def _mock_windows_color(val):
    return mock.patch.object(_windows_color, "terminal_supports_color", val)


def test_color_auto_is_true_for_tty():
    """Verify that color='auto' sets it to True for a tty."""
    with _mock_isatty(True), _mock_windows_color(True):
        formatter = base.BaseFormatter(options(color="auto"))
    assert formatter.color is True


def test_color_auto_is_false_without_tty():
    """Verify that color='auto' sets it to False without a tty."""
    with _mock_isatty(False), _mock_windows_color(True):
        formatter = base.BaseFormatter(options(color="auto"))
    assert formatter.color is False


def test_color_auto_is_false_if_not_supported_on_windows():
    """Verify that color='auto' is False if not supported on windows."""
    with _mock_isatty(True), _mock_windows_color(False):
        formatter = base.BaseFormatter(options(color="auto"))
    assert formatter.color is False


def test_color_never_is_false():
    """Verify that color='never' sets it to False despite a tty."""
    with _mock_isatty(True), _mock_windows_color(True):
        formatter = base.BaseFormatter(options(color="never"))
    assert formatter.color is False


class AfterInitFormatter(base.BaseFormatter):
    """Subclass for testing after_init."""

    def after_init(self):
        """Define method to verify operation."""
        self.post_initialized = True


def test_after_init_is_always_called():
    """Verify after_init is called."""
    formatter = AfterInitFormatter(options())
    assert formatter.post_initialized is True


class FormatFormatter(base.BaseFormatter):
    """Subclass for testing format."""

    def format(self, error):
        """Define method to verify operation."""
        return repr(error)


def test_handle_formats_the_error():
    """Verify that a formatter will call format from handle."""
    formatter = FormatFormatter(options(show_source=False))
    filemock = formatter.output_fd = mock.Mock()
    error = Violation(
        code="A001",
        filename="example.py",
        line_number=1,
        column_number=1,
        text="Fake error",
        physical_line="a = 1",
    )

    formatter.handle(error)

    filemock.write.assert_called_once_with(repr(error) + "\n")
