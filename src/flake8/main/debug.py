"""Module containing the logic for our debugging logic."""
import platform
from typing import Any
from typing import Dict
from typing import List

from flake8.plugins.manager import PluginTypeManager


def information(
    version: str,
    plugins: PluginTypeManager,
) -> Dict[str, Any]:
    """Generate the information to be printed for the bug report."""
    return {
        "version": version,
        "plugins": plugins_from(plugins),
        "platform": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "system": platform.system(),
        },
    }


def plugins_from(plugins: PluginTypeManager) -> List[Dict[str, str]]:
    """Generate the list of plugins installed."""
    return [
        {"plugin": name, "version": version}
        for name, version in sorted(set(plugins.manager.versions()))
    ]
