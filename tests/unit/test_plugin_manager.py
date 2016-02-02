"""Tests for flake8.plugins.manager.PluginManager."""
import mock

from flake8.plugins import manager


def create_entry_point_mock(name):
    """Create a mocked EntryPoint."""
    ep = mock.Mock(spec=['name'])
    ep.name = name
    return ep


@mock.patch('pkg_resources.iter_entry_points')
def test_calls_pkg_resources_on_instantiation(iter_entry_points):
    """Verify that we call iter_entry_points when we create a manager."""
    iter_entry_points.return_value = []
    manager.PluginManager(namespace='testing.pkg_resources')

    iter_entry_points.assert_called_once_with('testing.pkg_resources')


@mock.patch('pkg_resources.iter_entry_points')
def test_calls_pkg_resources_creates_plugins_automaticaly(iter_entry_points):
    """Verify that we create Plugins on instantiation."""
    iter_entry_points.return_value = [
        create_entry_point_mock('T100'),
        create_entry_point_mock('T200'),
    ]
    plugin_mgr = manager.PluginManager(namespace='testing.pkg_resources')

    iter_entry_points.assert_called_once_with('testing.pkg_resources')
    assert 'T100' in plugin_mgr.plugins
    assert 'T200' in plugin_mgr.plugins
    assert isinstance(plugin_mgr.plugins['T100'], manager.Plugin)
    assert isinstance(plugin_mgr.plugins['T200'], manager.Plugin)


@mock.patch('pkg_resources.iter_entry_points')
def test_handles_mapping_functions_across_plugins(iter_entry_points):
    """Verify we can use the PluginManager call functions on all plugins."""
    entry_point_mocks = [
        create_entry_point_mock('T100'),
        create_entry_point_mock('T200'),
    ]
    iter_entry_points.return_value = entry_point_mocks
    plugin_mgr = manager.PluginManager(namespace='testing.pkg_resources')
    plugins = [plugin_mgr.plugins[name] for name in plugin_mgr.names]

    assert list(plugin_mgr.map(lambda x: x)) == plugins
