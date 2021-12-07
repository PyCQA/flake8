"""Integration tests for plugin loading."""
from flake8.main import application
from flake8.main.cli import main

LOCAL_PLUGIN_CONFIG = "tests/fixtures/config_files/local-plugin.ini"
LOCAL_PLUGIN_PATH_CONFIG = "tests/fixtures/config_files/local-plugin-path.ini"


class ExtensionTestPlugin:
    """Extension test plugin."""

    name = "ExtensionTestPlugin"
    version = "1.0.0"

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""

    @classmethod
    def add_options(cls, parser):
        """Register options."""
        parser.add_option("--anopt")


class ReportTestPlugin:
    """Report test plugin."""

    name = "ReportTestPlugin"
    version = "1.0.0"

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""


def test_enable_local_plugin_from_config():
    """App can load a local plugin from config file."""
    app = application.Application()
    app.initialize(["flake8", "--config", LOCAL_PLUGIN_CONFIG])

    assert app.check_plugins is not None
    assert app.check_plugins["XE"].plugin is ExtensionTestPlugin
    assert app.formatting_plugins is not None
    assert app.formatting_plugins["XR"].plugin is ReportTestPlugin


def test_local_plugin_can_add_option():
    """A local plugin can add a CLI option."""
    app = application.Application()
    app.initialize(
        ["flake8", "--config", LOCAL_PLUGIN_CONFIG, "--anopt", "foo"]
    )

    assert app.options is not None
    assert app.options.anopt == "foo"


def test_enable_local_plugin_at_non_installed_path():
    """Can add a paths option in local-plugins config section for finding."""
    app = application.Application()
    app.initialize(["flake8", "--config", LOCAL_PLUGIN_PATH_CONFIG])

    assert app.check_plugins is not None
    assert app.check_plugins["XE"].plugin.name == "ExtensionTestPlugin2"


class AlwaysErrors:
    name = "AlwaysError"
    version = "1"

    def __init__(self, tree):
        pass

    def run(self):
        yield 1, 0, "ABC123 error", type(self)


class AlwaysErrorsDisabled(AlwaysErrors):
    off_by_default = True


def test_plugin_gets_enabled_by_default(tmp_path, capsys):
    cfg_s = f"""\
[flake8:local-plugins]
extension =
    ABC = {AlwaysErrors.__module__}:{AlwaysErrors.__name__}
"""
    cfg = tmp_path.joinpath("tox.ini")
    cfg.write_text(cfg_s)

    t_py = tmp_path.joinpath("t.py")
    t_py.touch()

    assert main((str(t_py), "--config", str(cfg))) == 1
    out, err = capsys.readouterr()
    assert out == f"{t_py}:1:1: ABC123 error\n"
    assert err == ""


def test_plugin_off_by_default(tmp_path, capsys):
    cfg_s = f"""\
[flake8:local-plugins]
extension =
    ABC = {AlwaysErrorsDisabled.__module__}:{AlwaysErrorsDisabled.__name__}
"""
    cfg = tmp_path.joinpath("tox.ini")
    cfg.write_text(cfg_s)

    t_py = tmp_path.joinpath("t.py")
    t_py.touch()

    cmd = (str(t_py), "--config", str(cfg))

    assert main(cmd) == 0
    out, err = capsys.readouterr()
    assert out == err == ""

    assert main((*cmd, "--enable-extension=ABC")) == 1
    out, err = capsys.readouterr()
    assert out == f"{t_py}:1:1: ABC123 error\n"
    assert err == ""
