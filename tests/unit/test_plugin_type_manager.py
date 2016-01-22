"""Tests for flake8.plugins.manager.PluginTypeManager."""
import collections
import mock

from flake8.plugins import manager

TEST_NAMESPACE = "testing.plugin-type-manager"


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
