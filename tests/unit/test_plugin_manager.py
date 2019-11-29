"""Tests for flake8.plugins.manager.PluginManager."""
import mock

from flake8._compat import importlib_metadata
from flake8.plugins import manager


@mock.patch.object(importlib_metadata, 'entry_points')
def test_calls_entrypoints_on_instantiation(entry_points_mck):
    """Verify that we call entry_points() when we create a manager."""
    entry_points_mck.return_value = {}
    manager.PluginManager(namespace='testing.entrypoints')
    entry_points_mck.assert_called_once_with()


@mock.patch.object(importlib_metadata, 'entry_points')
def test_calls_entrypoints_creates_plugins_automaticaly(entry_points_mck):
    """Verify that we create Plugins on instantiation."""
    entry_points_mck.return_value = {
        'testing.entrypoints': [
            importlib_metadata.EntryPoint('T100', '', None),
            importlib_metadata.EntryPoint('T200', '', None),
        ],
    }
    plugin_mgr = manager.PluginManager(namespace='testing.entrypoints')

    entry_points_mck.assert_called_once_with()
    assert 'T100' in plugin_mgr.plugins
    assert 'T200' in plugin_mgr.plugins
    assert isinstance(plugin_mgr.plugins['T100'], manager.Plugin)
    assert isinstance(plugin_mgr.plugins['T200'], manager.Plugin)


@mock.patch.object(importlib_metadata, 'entry_points')
def test_handles_mapping_functions_across_plugins(entry_points_mck):
    """Verify we can use the PluginManager call functions on all plugins."""
    entry_points_mck.return_value = {
        'testing.entrypoints': [
            importlib_metadata.EntryPoint('T100', '', None),
            importlib_metadata.EntryPoint('T200', '', None),
        ],
    }
    plugin_mgr = manager.PluginManager(namespace='testing.entrypoints')
    plugins = [plugin_mgr.plugins[name] for name in plugin_mgr.names]

    assert list(plugin_mgr.map(lambda x: x)) == plugins


@mock.patch.object(importlib_metadata, 'entry_points')
def test_local_plugins(entry_points_mck):
    """Verify PluginManager can load given local plugins."""
    entry_points_mck.return_value = {}
    plugin_mgr = manager.PluginManager(
        namespace='testing.entrypoints',
        local_plugins=['X = path.to:Plugin']
    )

    assert plugin_mgr.plugins['X'].entry_point.value == 'path.to:Plugin'
