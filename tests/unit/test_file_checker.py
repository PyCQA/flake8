"""Unit tests for the FileChecker class."""
from unittest import mock

import pytest

import flake8
from flake8 import checker


@mock.patch("flake8.checker.FileChecker._make_processor", return_value=None)
def test_repr(*args):
    """Verify we generate a correct repr."""
    file_checker = checker.FileChecker(
        "example.py",
        checks={},
        options=object(),
    )
    assert repr(file_checker) == "FileChecker for example.py"


def test_nonexistent_file():
    """Verify that checking non-existent file results in an error."""
    c = checker.FileChecker("foobar.py", checks={}, options=object())

    assert c.processor is None
    assert not c.should_process
    assert len(c.results) == 1
    error = c.results[0]
    assert error[0] == "E902"


def test_raises_exception_on_failed_plugin(tmp_path, default_options):
    """Checks that a failing plugin results in PluginExecutionFailed."""
    foobar = tmp_path / "foobar.py"
    foobar.write_text("I exist!")  # Create temp file
    plugin = {
        "name": "failure",
        "plugin_name": "failure",  # Both are necessary
        "parameters": dict(),
        "plugin": mock.MagicMock(side_effect=ValueError),
    }
    """Verify a failing plugin results in an plugin error"""
    fchecker = checker.FileChecker(
        str(foobar), checks=[], options=default_options
    )
    with pytest.raises(flake8.exceptions.PluginExecutionFailed):
        fchecker.run_check(plugin)
