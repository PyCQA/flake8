"""Tests for our debugging module."""
from unittest import mock

import pytest

from flake8.main import debug
from flake8.options import manager


@pytest.mark.parametrize(
    "plugins, expected",
    [
        ([], []),
        (
            [manager.PluginVersion("pycodestyle", "2.0.0", False)],
            [
                {
                    "plugin": "pycodestyle",
                    "version": "2.0.0",
                    "is_local": False,
                }
            ],
        ),
        (
            [
                manager.PluginVersion("pycodestyle", "2.0.0", False),
                manager.PluginVersion("mccabe", "0.5.9", False),
            ],
            [
                {"plugin": "mccabe", "version": "0.5.9", "is_local": False},
                {
                    "plugin": "pycodestyle",
                    "version": "2.0.0",
                    "is_local": False,
                },
            ],
        ),
        (
            [
                manager.PluginVersion("pycodestyle", "2.0.0", False),
                manager.PluginVersion("my-local", "0.0.1", True),
                manager.PluginVersion("mccabe", "0.5.9", False),
            ],
            [
                {"plugin": "mccabe", "version": "0.5.9", "is_local": False},
                {"plugin": "my-local", "version": "0.0.1", "is_local": True},
                {
                    "plugin": "pycodestyle",
                    "version": "2.0.0",
                    "is_local": False,
                },
            ],
        ),
    ],
)
def test_plugins_from(plugins, expected):
    """Test that we format plugins appropriately."""
    option_manager = mock.Mock(registered_plugins=set(plugins))
    assert expected == debug.plugins_from(option_manager)


@mock.patch("platform.python_implementation", return_value="CPython")
@mock.patch("platform.python_version", return_value="3.5.3")
@mock.patch("platform.system", return_value="Linux")
def test_information(system, pyversion, pyimpl):
    """Verify that we return all the information we care about."""
    expected = {
        "version": "3.1.0",
        "plugins": [
            {"plugin": "mccabe", "version": "0.5.9", "is_local": False},
            {"plugin": "pycodestyle", "version": "2.0.0", "is_local": False},
        ],
        "platform": {
            "python_implementation": "CPython",
            "python_version": "3.5.3",
            "system": "Linux",
        },
    }
    option_manager = mock.Mock(
        registered_plugins={
            manager.PluginVersion("pycodestyle", "2.0.0", False),
            manager.PluginVersion("mccabe", "0.5.9", False),
        },
        version="3.1.0",
    )
    assert expected == debug.information(option_manager)
    pyimpl.assert_called_once_with()
    pyversion.assert_called_once_with()
    system.assert_called_once_with()
