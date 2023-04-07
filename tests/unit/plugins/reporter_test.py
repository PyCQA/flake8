from __future__ import annotations

import argparse
import importlib.metadata

import pytest

from flake8.formatting import default
from flake8.plugins import finder
from flake8.plugins import reporter
from flake8.violation import Violation


def _opts(**kwargs):
    kwargs.setdefault("quiet", 0),
    kwargs.setdefault("color", "never")
    kwargs.setdefault("output_file", None)
    return argparse.Namespace(**kwargs)


@pytest.fixture
def violation():
    return Violation(
        code="E501",
        filename="test/test1.py",
        line_number=1,
        column_number=2,
        text="line too long (124 > 79 characters)",
        physical_line=None,
    )


@pytest.fixture
def reporters():
    def _plugin(name, cls):
        return finder.LoadedPlugin(
            finder.Plugin(
                "flake8",
                "123",
                importlib.metadata.EntryPoint(
                    name, f"{cls.__module__}:{cls.__name__}", "flake8.report"
                ),
            ),
            cls,
            {"options": True},
        )

    return {
        "default": _plugin("default", default.Default),
        "pylint": _plugin("pylint", default.Pylint),
        "github": _plugin("github", default.GitHub),
        "quiet-filename": _plugin("quiet-filename", default.FilenameOnly),
        "quiet-nothing": _plugin("quiet-nothing", default.Nothing),
    }


def test_make_formatter_default(reporters):
    ret = reporter.make(reporters, _opts(format="default"))
    assert isinstance(ret, default.Default)
    assert ret.error_format == default.Default.error_format


def test_make_formatter_quiet_filename(reporters):
    ret = reporter.make(reporters, _opts(format="default", quiet=1))
    assert isinstance(ret, default.FilenameOnly)


@pytest.mark.parametrize("quiet", (2, 3))
def test_make_formatter_very_quiet(reporters, quiet):
    ret = reporter.make(reporters, _opts(format="default", quiet=quiet))
    assert isinstance(ret, default.Nothing)


@pytest.mark.parametrize(
    "format_input, expected_formatter_class, error_str",
    [
        (
            "pylint",
            default.Pylint,
            "test/test1.py:1: [E501] line too long (124 > 79 characters)",
        ),
        (
            "github",
            default.GitHub,
            "::error title=Flake8 E501,file=test/test1.py,line=1,col=2,endLine=1,endColumn=2::E501 line too long (124 > 79 characters)",  # noqa: E501
        ),
    ],
)
def test_make_formatter_custom(
    reporters, violation, format_input, expected_formatter_class, error_str
):
    ret = reporter.make(reporters, _opts(format=format_input))
    assert isinstance(ret, expected_formatter_class)
    assert ret.format(violation) == error_str


def test_make_formatter_format_string(reporters, caplog):
    ret = reporter.make(reporters, _opts(format="hi %(code)s"))
    assert isinstance(ret, default.Default)
    assert ret.error_format == "hi %(code)s"

    assert caplog.record_tuples == [
        (
            "flake8.plugins.reporter",
            30,
            "'hi %(code)s' is an unknown formatter.  Falling back to default.",
        )
    ]
