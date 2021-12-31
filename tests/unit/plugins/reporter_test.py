import argparse

import pytest

from flake8._compat import importlib_metadata
from flake8.formatting import default
from flake8.plugins import finder
from flake8.plugins import reporter


def _opts(**kwargs):
    kwargs.setdefault("quiet", 0),
    kwargs.setdefault("color", "never")
    kwargs.setdefault("output_file", None)
    return argparse.Namespace(**kwargs)


@pytest.fixture
def reporters():
    def _plugin(name, cls):
        return finder.LoadedPlugin(
            finder.Plugin(
                "flake8",
                "123",
                importlib_metadata.EntryPoint(
                    name, f"{cls.__module__}:{cls.__name__}", "flake8.report"
                ),
            ),
            cls,
            {"options": True},
        )

    return {
        "default": _plugin("default", default.Default),
        "pylint": _plugin("pylint", default.Pylint),
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


def test_make_formatter_custom(reporters):
    ret = reporter.make(reporters, _opts(format="pylint"))
    assert isinstance(ret, default.Pylint)


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
