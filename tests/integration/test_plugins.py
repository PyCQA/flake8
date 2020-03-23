"""Integration tests for plugin loading."""
from flake8.main import application


LOCAL_PLUGIN_CONFIG = 'tests/fixtures/config_files/local-plugin.ini'
LOCAL_PLUGIN_PATH_CONFIG = 'tests/fixtures/config_files/local-plugin-path.ini'


class ExtensionTestPlugin(object):
    """Extension test plugin."""

    name = 'ExtensionTestPlugin'
    version = '1.0.0'

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""

    @classmethod
    def add_options(cls, parser):
        """Register options."""
        parser.add_option('--anopt')


class ReportTestPlugin(object):
    """Report test plugin."""

    name = 'ReportTestPlugin'
    version = '1.0.0'

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""


def test_enable_local_plugin_from_config():
    """App can load a local plugin from config file."""
    app = application.Application()
    app.initialize(['flake8', '--config', LOCAL_PLUGIN_CONFIG])

    assert app.check_plugins['XE'].plugin is ExtensionTestPlugin
    assert app.formatting_plugins['XR'].plugin is ReportTestPlugin


def test_local_plugin_can_add_option():
    """A local plugin can add a CLI option."""
    app = application.Application()
    app.initialize(
        ['flake8', '--config', LOCAL_PLUGIN_CONFIG, '--anopt', 'foo'])

    assert app.options.anopt == 'foo'


def test_enable_local_plugin_at_non_installed_path():
    """Can add a paths option in local-plugins config section for finding."""
    app = application.Application()
    app.initialize(['flake8', '--config', LOCAL_PLUGIN_PATH_CONFIG])

    assert app.check_plugins['XE'].plugin.name == 'ExtensionTestPlugin2'
