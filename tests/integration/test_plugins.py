"""Integration tests for plugin loading."""
import pytest

from flake8.main.cli import main
from flake8.main.options import register_default_options
from flake8.main.options import stage1_arg_parser
from flake8.options import aggregator
from flake8.options import config
from flake8.options.manager import OptionManager
from flake8.plugins import finder


class ExtensionTestPlugin:
    """Extension test plugin."""

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

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""


@pytest.fixture
def local_config(tmp_path):
    cfg_s = f"""\
[flake8:local-plugins]
extension =
    XE = {ExtensionTestPlugin.__module__}:{ExtensionTestPlugin.__name__}
report =
    XR = {ReportTestPlugin.__module__}:{ReportTestPlugin.__name__}
"""
    cfg = tmp_path.joinpath("tox.ini")
    cfg.write_text(cfg_s)

    return str(cfg)


def test_enable_local_plugin_from_config(local_config):
    """App can load a local plugin from config file."""
    cfg, cfg_dir = config.load_config(local_config, [], isolated=False)
    plugins = finder.find_plugins(cfg)
    plugin_paths = finder.find_local_plugin_paths(cfg, cfg_dir)
    opts = finder.PluginOptions(frozenset())
    loaded_plugins = finder.load_plugins(plugins, plugin_paths, opts)

    (custom_extension,) = (
        loaded
        for loaded in loaded_plugins.checkers.tree
        if loaded.entry_name == "XE"
    )
    custom_report = loaded_plugins.reporters["XR"]

    assert custom_extension.obj is ExtensionTestPlugin
    assert custom_report.obj is ReportTestPlugin


def test_local_plugin_can_add_option(local_config):
    """A local plugin can add a CLI option."""

    argv = ["--config", local_config, "--anopt", "foo"]

    stage1_parser = stage1_arg_parser()
    stage1_args, rest = stage1_parser.parse_known_args(argv)

    cfg, cfg_dir = config.load_config(
        config=stage1_args.config, extra=[], isolated=False
    )

    plugins = finder.find_plugins(cfg)
    plugin_paths = finder.find_local_plugin_paths(cfg, cfg_dir)
    opts = finder.PluginOptions(frozenset())
    loaded_plugins = finder.load_plugins(plugins, plugin_paths, opts)

    option_manager = OptionManager(
        version="123",
        plugin_versions="",
        parents=[stage1_parser],
    )
    register_default_options(option_manager)
    option_manager.register_plugins(loaded_plugins)

    args = aggregator.aggregate_options(option_manager, cfg, cfg_dir, argv)

    assert args.extended_default_select == {"XE", "F", "E", "C90"}
    assert args.anopt == "foo"


class AlwaysErrors:
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
