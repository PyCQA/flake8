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
