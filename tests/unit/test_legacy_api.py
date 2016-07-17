"""Tests for Flake8's legacy API."""
import mock

from flake8.api import legacy as api


def test_get_style_guide():
    """Verify the methods called on our internal Application."""
    mockedapp = mock.Mock()
    with mock.patch('flake8.main.application.Application') as Application:
        Application.return_value = mockedapp
        style_guide = api.get_style_guide()

    Application.assert_called_once_with()
    mockedapp.find_plugins.assert_called_once_with()
    mockedapp.register_plugin_options.assert_called_once_with()
    mockedapp.parse_configuration_and_cli.assert_called_once_with([])
    mockedapp.make_formatter.assert_called_once_with()
    mockedapp.make_notifier.assert_called_once_with()
    mockedapp.make_guide.assert_called_once_with()
    mockedapp.make_file_checker_manager.assert_called_once_with()
    assert isinstance(style_guide, api.StyleGuide)


def test_styleguide_options():
    """Show tha we proxy the StyleGuide.options attribute."""
    app = mock.Mock()
    app.options = 'options'
    style_guide = api.StyleGuide(app)
    assert style_guide.options == 'options'


def test_styleguide_paths():
    """Show tha we proxy the StyleGuide.paths attribute."""
    app = mock.Mock()
    app.paths = 'paths'
    style_guide = api.StyleGuide(app)
    assert style_guide.paths == 'paths'


def test_styleguide_check_files():
    """Verify we call the right application methods."""
    paths = ['foo', 'bar']
    app = mock.Mock()
    style_guide = api.StyleGuide(app)
    report = style_guide.check_files(paths)

    app.run_checks.assert_called_once_with(paths)
    app.report_errors.assert_called_once_with()
    assert isinstance(report, api.Report)
