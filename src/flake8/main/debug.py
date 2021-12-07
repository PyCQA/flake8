"""Module containing the logic for our debugging logic."""
import platform


def information(option_manager):
    """Generate the information to be printed for the bug report."""
    return {
        "version": option_manager.version,
        "plugins": plugins_from(option_manager),
        "platform": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "system": platform.system(),
        },
    }


def plugins_from(option_manager):
    """Generate the list of plugins installed."""
    return [
        {
            "plugin": plugin.name,
            "version": plugin.version,
            "is_local": plugin.local,
        }
        for plugin in sorted(option_manager.registered_plugins)
    ]
