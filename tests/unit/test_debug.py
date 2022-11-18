from __future__ import annotations

import importlib.metadata
from unittest import mock

from flake8.main import debug
from flake8.plugins import finder


def test_debug_information():
    def _plugin(pkg, version, ep_name):
        return finder.LoadedPlugin(
            finder.Plugin(
                pkg,
                version,
                importlib.metadata.EntryPoint(
                    ep_name, "dne:dne", "flake8.extension"
                ),
            ),
            None,
            {},
        )

    plugins = finder.Plugins(
        checkers=finder.Checkers(
            tree=[
                _plugin("pkg1", "1.2.3", "X1"),
                _plugin("pkg1", "1.2.3", "X2"),
                _plugin("pkg2", "4.5.6", "X3"),
            ],
            logical_line=[],
            physical_line=[],
        ),
        reporters={},
        disabled=[],
    )

    info = debug.information("9001", plugins)
    assert info == {
        "version": "9001",
        "plugins": [
            {"plugin": "pkg1", "version": "1.2.3"},
            {"plugin": "pkg2", "version": "4.5.6"},
        ],
        "platform": {
            "python_implementation": mock.ANY,
            "python_version": mock.ANY,
            "system": mock.ANY,
        },
    }
