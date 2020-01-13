"""Tests for get_local_plugins."""
import mock

from flake8.options import config


def test_get_local_plugins_respects_isolated():
    """Verify behaviour of get_local_plugins with isolated=True."""
    config_finder = mock.MagicMock()
    config_finder.ignore_config_files = True

    local_plugins = config.get_local_plugins(config_finder)

    assert local_plugins.extension == []
    assert local_plugins.report == []
    assert config_finder.local_configs.called is False
    assert config_finder.user_config.called is False


def test_get_local_plugins_uses_cli_config():
    """Verify behaviour of get_local_plugins with a specified config."""
    config_obj = mock.Mock()
    config_finder = mock.MagicMock()
    config_finder.cli_config.return_value = config_obj
    config_finder.ignore_config_files = False
    config_obj.get.return_value = ''
    config_file_value = 'foo.ini'
    config_finder.config_file = config_file_value

    config.get_local_plugins(config_finder)

    config_finder.cli_config.assert_called_once_with(config_file_value)


def test_get_local_plugins():
    """Verify get_local_plugins returns expected plugins."""
    config_fixture_path = 'tests/fixtures/config_files/local-plugin.ini'
    config_finder = config.ConfigFileFinder('flake8')

    with mock.patch.object(config_finder, 'local_config_files') as localcfs:
        localcfs.return_value = [config_fixture_path]
        local_plugins = config.get_local_plugins(config_finder)

    assert local_plugins.extension == ['XE = test_plugins:ExtensionTestPlugin']
    assert local_plugins.report == ['XR = test_plugins:ReportTestPlugin']
