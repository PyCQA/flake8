"""Tests for our debugging module."""
from unittest import mock

import pytest

from flake8.main import debug


@pytest.mark.parametrize(
    ("versions", "expected"),
    (
        ([], []),
        (
            [("p1", "1"), ("p2", "2"), ("p1", "1")],
            [
                {"plugin": "p1", "version": "1"},
                {"plugin": "p2", "version": "2"},
            ],
        ),
    ),
)
def test_plugins_from(versions, expected):
    """Test that we format plugins appropriately."""
    option_manager = mock.Mock(**{"manager.versions.return_value": versions})
    assert expected == debug.plugins_from(option_manager)


@mock.patch("platform.python_implementation", return_value="CPython")
@mock.patch("platform.python_version", return_value="3.5.3")
@mock.patch("platform.system", return_value="Linux")
def test_information(system, pyversion, pyimpl):
    """Verify that we return all the information we care about."""
    expected = {
        "version": "3.1.0",
        "plugins": [
            {"plugin": "mccabe", "version": "0.5.9"},
            {"plugin": "pycodestyle", "version": "2.0.0"},
        ],
        "platform": {
            "python_implementation": "CPython",
            "python_version": "3.5.3",
            "system": "Linux",
        },
    }
    plugins = mock.Mock(
        **{
            "manager.versions.return_value": [
                ("pycodestyle", "2.0.0"),
                ("mccabe", "0.5.9"),
            ]
        }
    )
    assert expected == debug.information("3.1.0", plugins)
    pyimpl.assert_called_once_with()
    pyversion.assert_called_once_with()
    system.assert_called_once_with()
