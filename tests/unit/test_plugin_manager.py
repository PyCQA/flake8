"""Tests for flake8.plugins.manager.PluginManager."""
import mock

from flake8.plugins import manager


def create_entry_point_mock(name):
    """Create a mocked EntryPoint."""
    ep = mock.Mock(spec=['name'])
    ep.name = name
    return ep


@mock.patch('entrypoints.get_group_all')
def test_calls_entrypoints_on_instantiation(get_group_all):
    """Verify that we call get_group_all when we create a manager."""
    get_group_all.return_value = []
    manager.PluginManager(namespace='testing.entrypoints')

    get_group_all.assert_called_once_with('testing.entrypoints')


@mock.patch('entrypoints.get_group_all')
def test_calls_entrypoints_creates_plugins_automaticaly(get_group_all):
    """Verify that we create Plugins on instantiation."""
    get_group_all.return_value = [
        create_entry_point_mock('T100'),
        create_entry_point_mock('T200'),
    ]
    plugin_mgr = manager.PluginManager(namespace='testing.entrypoints')

    get_group_all.assert_called_once_with('testing.entrypoints')
    assert 'T100' in plugin_mgr.plugins
    assert 'T200' in plugin_mgr.plugins
    assert isinstance(plugin_mgr.plugins['T100'], manager.Plugin)
    assert isinstance(plugin_mgr.plugins['T200'], manager.Plugin)


@mock.patch('entrypoints.get_group_all')
def test_handles_mapping_functions_across_plugins(get_group_all):
    """Verify we can use the PluginManager call functions on all plugins."""
    entry_point_mocks = [
        create_entry_point_mock('T100'),
        create_entry_point_mock('T200'),
    ]
    get_group_all.return_value = entry_point_mocks
    plugin_mgr = manager.PluginManager(namespace='testing.entrypoints')
    plugins = [plugin_mgr.plugins[name] for name in plugin_mgr.names]

    assert list(plugin_mgr.map(lambda x: x)) == plugins


@mock.patch('entrypoints.get_group_all')
def test_local_plugins(get_group_all):
    """Verify PluginManager can load given local plugins."""
    get_group_all.return_value = []
    plugin_mgr = manager.PluginManager(
        namespace='testing.entrypoints',
        local_plugins=['X = path.to:Plugin']
    )

    assert plugin_mgr.plugins['X'].entry_point.module_name == 'path.to'
