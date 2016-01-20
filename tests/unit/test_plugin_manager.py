"""Tests for flake8.plugins.manager.PluginManager."""
import mock

from flake8.plugins import manager


@mock.patch('pkg_resources.iter_entry_points')
def test_calls_pkg_resources_on_instantiation(iter_entry_points):
    """Verify that we call iter_entry_points when we create a manager."""
    iter_entry_points.return_value = []
    manager.PluginManager(namespace='testing.pkg_resources')

    iter_entry_points.assert_called_once_with('testing.pkg_resources')
