"""Tests for Flake8's legacy API."""
from __future__ import annotations

from unittest import mock

import pytest

from flake8.api import legacy as api
from flake8.formatting import base as formatter


def test_styleguide_options():
    """Show that we proxy the StyleGuide.options attribute."""
    app = mock.Mock()
    app.options = "options"
    style_guide = api.StyleGuide(app)
    assert style_guide.options == "options"


def test_styleguide_paths():
    """Show that we proxy the StyleGuide.paths attribute."""
    app = mock.Mock()
    app.options.filenames = ["paths"]
    style_guide = api.StyleGuide(app)
    assert style_guide.paths == ["paths"]


def test_styleguide_check_files():
    """Verify we call the right application methods."""
    paths = ["foo", "bar"]
    app = mock.Mock()
    style_guide = api.StyleGuide(app)
    report = style_guide.check_files(paths)

    assert app.options.filenames == paths
    app.run_checks.assert_called_once_with()
    app.report_errors.assert_called_once_with()
    assert isinstance(report, api.Report)


def test_styleguide_excluded():
    """Verify we delegate to our file checker manager.

    When we add the parent argument, we don't check that is_path_excluded was
    called only once.
    """
    style_guide = api.get_style_guide(exclude=["file*", "*/parent/*"])
    assert not style_guide.excluded("unrelated.py")
    assert style_guide.excluded("file.py")
    assert style_guide.excluded("test.py", "parent")


def test_styleguide_init_report_does_nothing():
    """Verify if we use None that we don't call anything."""
    app = mock.Mock()
    style_guide = api.StyleGuide(app)
    style_guide.init_report()
    assert app.make_formatter.called is False
    assert app.make_guide.called is False


def test_styleguide_init_report_with_non_subclass():
    """Verify we raise a ValueError with non BaseFormatter subclasses."""
    app = mock.Mock()
    style_guide = api.StyleGuide(app)
    with pytest.raises(ValueError):
        style_guide.init_report(object)  # type: ignore
    assert app.make_formatter.called is False
    assert app.make_guide.called is False


def test_styleguide_init_report():
    """Verify we do the right incantation for the Application."""
    app = mock.Mock(guide="fake")
    style_guide = api.StyleGuide(app)

    class FakeFormatter(formatter.BaseFormatter):
        def format(self, *args):
            raise NotImplementedError

    style_guide.init_report(FakeFormatter)
    assert isinstance(app.formatter, FakeFormatter)
    assert app.guide is None
    app.make_guide.assert_called_once_with()


def test_styleguide_input_file():
    """Verify we call StyleGuide.check_files with the filename."""
    app = mock.Mock()
    style_guide = api.StyleGuide(app)
    with mock.patch.object(style_guide, "check_files") as check_files:
        style_guide.input_file("file.py")
    check_files.assert_called_once_with(["file.py"])


def test_report_total_errors():
    """Verify total errors is just a proxy attribute."""
    app = mock.Mock(result_count="Fake count")
    report = api.Report(app)
    assert report.total_errors == "Fake count"


def test_report_get_statistics():
    """Verify that we use the statistics object."""
    stats = mock.Mock()
    stats.statistics_for.return_value = []
    style_guide = mock.Mock(stats=stats)
    app = mock.Mock(guide=style_guide)

    report = api.Report(app)
    assert report.get_statistics("E") == []
    stats.statistics_for.assert_called_once_with("E")
