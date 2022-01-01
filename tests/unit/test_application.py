"""Tests for the Application class."""
import argparse

import pytest

from flake8.main import application as app


def options(**kwargs):
    """Generate argparse.Namespace for our Application."""
    kwargs.setdefault("verbose", 0)
    kwargs.setdefault("output_file", None)
    kwargs.setdefault("count", False)
    kwargs.setdefault("exit_zero", False)
    return argparse.Namespace(**kwargs)


@pytest.fixture
def application():
    """Create an application."""
    return app.Application()


@pytest.mark.parametrize(
    "result_count, catastrophic, exit_zero, value",
    [
        (0, False, False, 0),
        (0, True, False, 1),
        (2, False, False, 1),
        (2, True, False, 1),
        (0, True, True, 1),
        (2, False, True, 0),
        (2, True, True, 1),
    ],
)
def test_application_exit_code(
    result_count, catastrophic, exit_zero, value, application
):
    """Verify Application.exit_code returns the correct value."""
    application.result_count = result_count
    application.catastrophic_failure = catastrophic
    application.options = options(exit_zero=exit_zero)

    assert application.exit_code() == value
