"""Tests for flake8.plugins.manager.PluginTypeManager."""
import collections

import mock
import pytest

from flake8 import exceptions
from flake8.plugins import manager

TEST_NAMESPACE = "testing.plugin-type-manager"


def create_plugin_mock(raise_exception=False):
    """Create an auto-spec'd mock of a flake8 Plugin."""
    plugin = mock.create_autospec(manager.Plugin, instance=True)
    if raise_exception:
        plugin.load_plugin.side_effect = exceptions.FailedToLoadPlugin(
            plugin=mock.Mock(name='T101'),
            exception=ValueError('Test failure'),
        )
    return plugin


class TestType(manager.PluginTypeManager):
    """Fake PluginTypeManager."""

    namespace = TEST_NAMESPACE


@mock.patch('flake8.plugins.manager.PluginManager')
def test_instantiates_a_manager(PluginManager):
    """Verify we create a PluginManager on instantiation."""
    TestType()

    PluginManager.assert_called_once_with(TEST_NAMESPACE)


@mock.patch('flake8.plugins.manager.PluginManager')
def test_proxies_names_to_manager(PluginManager):
    """Verify we proxy the names attribute."""
    PluginManager.return_value = mock.Mock(names=[
        'T100', 'T200', 'T300'
    ])
    type_mgr = TestType()

    assert type_mgr.names == ['T100', 'T200', 'T300']


@mock.patch('flake8.plugins.manager.PluginManager')
def test_proxies_plugins_to_manager(PluginManager):
    """Verify we proxy the plugins attribute."""
    PluginManager.return_value = mock.Mock(plugins=[
        'T100', 'T200', 'T300'
    ])
    type_mgr = TestType()

    assert type_mgr.plugins == ['T100', 'T200', 'T300']


def test_generate_call_function():
    """Verify the function we generate."""
    optmanager = object()
    plugin = mock.Mock(method_name=lambda x: x)
    func = manager.PluginTypeManager._generate_call_function(
        'method_name', optmanager,
    )

    assert isinstance(func, collections.Callable)
    assert func(plugin) is optmanager


@mock.patch('flake8.plugins.manager.PluginManager')
def test_load_plugins(PluginManager):
    """Verify load plugins loads *every* plugin."""
    # Create a bunch of fake plugins
    plugins = [create_plugin_mock(), create_plugin_mock(),
               create_plugin_mock(), create_plugin_mock(),
               create_plugin_mock(), create_plugin_mock(),
               create_plugin_mock(), create_plugin_mock()]

    # Have a function that will actually call the method underneath
    def fake_map(func):
        for plugin in plugins:
            yield func(plugin)

    # Mock out the PluginManager instance
    manager_mock = mock.Mock(spec=['map'])
    # Replace the map method
    manager_mock.map = fake_map
    # Return our PluginManager mock
    PluginManager.return_value = manager_mock

    type_mgr = TestType()
    # Load the tests (do what we're actually testing)
    assert len(type_mgr.load_plugins()) == 8
    # Assert that our closure does what we think it does
    for plugin in plugins:
        plugin.load_plugin.assert_called_once_with()
    assert type_mgr.plugins_loaded is True


@mock.patch('flake8.plugins.manager.PluginManager')
def test_load_plugins_fails(PluginManager):
    """Verify load plugins bubbles up exceptions."""
    plugins = [create_plugin_mock(), create_plugin_mock(True),
               create_plugin_mock(), create_plugin_mock(),
               create_plugin_mock(), create_plugin_mock(),
               create_plugin_mock(), create_plugin_mock()]

    # Have a function that will actually call the method underneath
    def fake_map(func):
        for plugin in plugins:
            yield func(plugin)

    # Mock out the PluginManager instance
    manager_mock = mock.Mock(spec=['map'])
    # Replace the map method
    manager_mock.map = fake_map
    # Return our PluginManager mock
    PluginManager.return_value = manager_mock

    type_mgr = TestType()
    with pytest.raises(exceptions.FailedToLoadPlugin):
        type_mgr.load_plugins()

    # Assert we didn't finish loading plugins
    assert type_mgr.plugins_loaded is False
    # Assert the first two plugins had their load_plugin method called
    plugins[0].load_plugin.assert_called_once_with()
    plugins[1].load_plugin.assert_called_once_with()
    # Assert the rest of the plugins were not loaded
    for plugin in plugins[2:]:
        assert plugin.load_plugin.called is False
