import configparser
import sys
from unittest import mock

import pytest

from flake8._compat import importlib_metadata
from flake8.exceptions import FailedToLoadPlugin
from flake8.plugins import finder
from flake8.plugins.pyflakes import FlakesChecker


def _ep(name="X", value="dne:dne", group="flake8.extension"):
    return importlib_metadata.EntryPoint(name, value, group)


def _plugin(package="local", version="local", ep=None):
    if ep is None:
        ep = _ep()
    return finder.Plugin(package, version, ep)


def _loaded(plugin=None, obj=None, parameters=None):
    if plugin is None:
        plugin = _plugin()
    if parameters is None:
        parameters = {"tree": True}
    return finder.LoadedPlugin(plugin, obj, parameters)


def test_loaded_plugin_entry_name_vs_display_name():
    loaded = _loaded(_plugin(package="package-name", ep=_ep(name="Q")))
    assert loaded.entry_name == "Q"
    assert loaded.display_name == "package-name[Q]"


def test_plugins_all_plugins():
    tree_plugin = _loaded(parameters={"tree": True})
    logical_line_plugin = _loaded(parameters={"logical_line": True})
    physical_line_plugin = _loaded(parameters={"physical_line": True})
    report_plugin = _loaded(
        plugin=_plugin(ep=_ep(name="R", group="flake8.report"))
    )

    plugins = finder.Plugins(
        checkers=finder.Checkers(
            tree=[tree_plugin],
            logical_line=[logical_line_plugin],
            physical_line=[physical_line_plugin],
        ),
        reporters={"R": report_plugin},
        disabled=[],
    )

    assert tuple(plugins.all_plugins()) == (
        tree_plugin,
        logical_line_plugin,
        physical_line_plugin,
        report_plugin,
    )


def test_plugins_versions_str():
    plugins = finder.Plugins(
        checkers=finder.Checkers(
            tree=[_loaded(_plugin(package="pkg1", version="1"))],
            logical_line=[_loaded(_plugin(package="pkg2", version="2"))],
            physical_line=[_loaded(_plugin(package="pkg1", version="1"))],
        ),
        reporters={
            # ignore flake8 builtin plugins
            "default": _loaded(_plugin(package="flake8")),
            # ignore local plugins
            "custom": _loaded(_plugin(package="local")),
        },
        disabled=[],
    )
    assert plugins.versions_str() == "pkg1: 1, pkg2: 2"


@pytest.fixture
def pyflakes_dist(tmp_path):
    metadata = """\
Metadata-Version: 2.1
Name: pyflakes
Version: 9000.1.0
"""
    d = tmp_path.joinpath("pyflakes.dist-info")
    d.mkdir()
    d.joinpath("METADATA").write_text(metadata)
    return importlib_metadata.PathDistribution(d)


@pytest.fixture
def pycodestyle_dist(tmp_path):
    metadata = """\
Metadata-Version: 2.1
Name: pycodestyle
Version: 9000.2.0
"""
    d = tmp_path.joinpath("pycodestyle.dist-info")
    d.mkdir()
    d.joinpath("METADATA").write_text(metadata)
    return importlib_metadata.PathDistribution(d)


@pytest.fixture
def flake8_dist(tmp_path):
    metadata = """\
Metadata-Version: 2.1
Name: flake8
Version: 9001
"""
    entry_points = """\
[console_scripts]
flake8 = flake8.main.cli:main

[flake8.extension]
F = flake8.plugins.pyflakes:FlakesChecker
pycodestyle.bare_except = pycodestyle:bare_except
pycodestyle.blank_lines = pycodestyle:blank_lines

[flake8.report]
default = flake8.formatting.default:Default
pylint = flake8.formatting.default:Pylint
"""
    d = tmp_path.joinpath("flake8.dist-info")
    d.mkdir()
    d.joinpath("METADATA").write_text(metadata)
    d.joinpath("entry_points.txt").write_text(entry_points)
    return importlib_metadata.PathDistribution(d)


@pytest.fixture
def flake8_foo_dist(tmp_path):
    metadata = """\
Metadata-Version: 2.1
Name: flake8-foo
Version: 1.2.3
"""
    eps = """\
[console_scripts]
foo = flake8_foo:main
[flake8.extension]
Q = flake8_foo:Plugin
[flake8.report]
foo = flake8_foo:Formatter
"""
    d = tmp_path.joinpath("flake8_foo.dist-info")
    d.mkdir()
    d.joinpath("METADATA").write_text(metadata)
    d.joinpath("entry_points.txt").write_text(eps)
    return importlib_metadata.PathDistribution(d)


@pytest.fixture
def mock_distribution(pyflakes_dist, pycodestyle_dist):
    dists = {"pyflakes": pyflakes_dist, "pycodestyle": pycodestyle_dist}
    with mock.patch.object(importlib_metadata, "distribution", dists.get):
        yield


def test_flake8_plugins(flake8_dist, mock_distribution):
    """Ensure entrypoints for flake8 are parsed specially."""

    eps = flake8_dist.entry_points
    ret = set(finder._flake8_plugins(eps, "flake8", "9001"))
    assert ret == {
        finder.Plugin(
            "pyflakes",
            "9000.1.0",
            importlib_metadata.EntryPoint(
                "F",
                "flake8.plugins.pyflakes:FlakesChecker",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "pycodestyle",
            "9000.2.0",
            importlib_metadata.EntryPoint(
                "pycodestyle.bare_except",
                "pycodestyle:bare_except",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "pycodestyle",
            "9000.2.0",
            importlib_metadata.EntryPoint(
                "pycodestyle.blank_lines",
                "pycodestyle:blank_lines",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "flake8",
            "9001",
            importlib_metadata.EntryPoint(
                "default", "flake8.formatting.default:Default", "flake8.report"
            ),
        ),
        finder.Plugin(
            "flake8",
            "9001",
            importlib_metadata.EntryPoint(
                "pylint", "flake8.formatting.default:Pylint", "flake8.report"
            ),
        ),
    }


def test_importlib_plugins(
    tmp_path,
    flake8_dist,
    flake8_foo_dist,
    mock_distribution,
    caplog,
):
    """Ensure we can load plugins from importlib_metadata."""

    # make sure flake8-colors is skipped
    flake8_colors_metadata = """\
Metadata-Version: 2.1
Name: flake8-colors
Version: 1.2.3
"""
    flake8_colors_eps = """\
[flake8.extension]
flake8-colors = flake8_colors:ColorFormatter
"""
    flake8_colors_d = tmp_path.joinpath("flake8_colors.dist-info")
    flake8_colors_d.mkdir()
    flake8_colors_d.joinpath("METADATA").write_text(flake8_colors_metadata)
    flake8_colors_d.joinpath("entry_points.txt").write_text(flake8_colors_eps)
    flake8_colors_dist = importlib_metadata.PathDistribution(flake8_colors_d)

    unrelated_metadata = """\
Metadata-Version: 2.1
Name: unrelated
Version: 4.5.6
"""
    unrelated_eps = """\
[console_scripts]
unrelated = unrelated:main
"""
    unrelated_d = tmp_path.joinpath("unrelated.dist-info")
    unrelated_d.mkdir()
    unrelated_d.joinpath("METADATA").write_text(unrelated_metadata)
    unrelated_d.joinpath("entry_points.txt").write_text(unrelated_eps)
    unrelated_dist = importlib_metadata.PathDistribution(unrelated_d)

    with mock.patch.object(
        importlib_metadata,
        "distributions",
        return_value=[
            flake8_dist,
            flake8_colors_dist,
            flake8_foo_dist,
            unrelated_dist,
        ],
    ):
        ret = set(finder._find_importlib_plugins())

    assert ret == {
        finder.Plugin(
            "flake8-foo",
            "1.2.3",
            importlib_metadata.EntryPoint(
                "Q", "flake8_foo:Plugin", "flake8.extension"
            ),
        ),
        finder.Plugin(
            "pycodestyle",
            "9000.2.0",
            importlib_metadata.EntryPoint(
                "pycodestyle.bare_except",
                "pycodestyle:bare_except",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "pycodestyle",
            "9000.2.0",
            importlib_metadata.EntryPoint(
                "pycodestyle.blank_lines",
                "pycodestyle:blank_lines",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "pyflakes",
            "9000.1.0",
            importlib_metadata.EntryPoint(
                "F",
                "flake8.plugins.pyflakes:FlakesChecker",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "flake8",
            "9001",
            importlib_metadata.EntryPoint(
                "default", "flake8.formatting.default:Default", "flake8.report"
            ),
        ),
        finder.Plugin(
            "flake8",
            "9001",
            importlib_metadata.EntryPoint(
                "pylint", "flake8.formatting.default:Pylint", "flake8.report"
            ),
        ),
        finder.Plugin(
            "flake8-foo",
            "1.2.3",
            importlib_metadata.EntryPoint(
                "foo", "flake8_foo:Formatter", "flake8.report"
            ),
        ),
    }

    assert caplog.record_tuples == [
        (
            "flake8.plugins.finder",
            30,
            "flake8-colors plugin is obsolete in flake8>=4.1",
        ),
    ]


def test_find_local_plugins_nothing():
    cfg = configparser.RawConfigParser()
    assert set(finder._find_local_plugins(cfg)) == set()


@pytest.fixture
def local_plugin_cfg():
    cfg = configparser.RawConfigParser()
    cfg.add_section("flake8:local-plugins")
    cfg.set("flake8:local-plugins", "extension", "Y=mod2:attr, X = mod:attr")
    cfg.set("flake8:local-plugins", "report", "Z=mod3:attr")
    return cfg


def test_find_local_plugins(local_plugin_cfg):
    ret = set(finder._find_local_plugins(local_plugin_cfg))
    assert ret == {
        finder.Plugin(
            "local",
            "local",
            importlib_metadata.EntryPoint(
                "X",
                "mod:attr",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "local",
            "local",
            importlib_metadata.EntryPoint(
                "Y",
                "mod2:attr",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "local",
            "local",
            importlib_metadata.EntryPoint(
                "Z",
                "mod3:attr",
                "flake8.report",
            ),
        ),
    }


def test_parse_enabled_not_specified():
    assert finder.parse_enabled(configparser.RawConfigParser(), None) == set()


def test_parse_enabled_from_commandline():
    cfg = configparser.RawConfigParser()
    cfg.add_section("flake8")
    cfg.set("flake8", "enable_extensions", "A,B,C")
    assert finder.parse_enabled(cfg, "D,E,F") == {"D", "E", "F"}


@pytest.mark.parametrize("opt", ("enable_extensions", "enable-extensions"))
def test_parse_enabled_from_config(opt):
    cfg = configparser.RawConfigParser()
    cfg.add_section("flake8")
    cfg.set("flake8", opt, "A,B,C")
    assert finder.parse_enabled(cfg, None) == {"A", "B", "C"}


def test_find_plugins(
    tmp_path,
    flake8_dist,
    flake8_foo_dist,
    mock_distribution,
    local_plugin_cfg,
):
    with mock.patch.object(
        importlib_metadata,
        "distributions",
        return_value=[flake8_dist, flake8_foo_dist],
    ):
        ret = finder.find_plugins(local_plugin_cfg)

    assert ret == [
        finder.Plugin(
            "flake8",
            "9001",
            importlib_metadata.EntryPoint(
                "default", "flake8.formatting.default:Default", "flake8.report"
            ),
        ),
        finder.Plugin(
            "flake8",
            "9001",
            importlib_metadata.EntryPoint(
                "pylint", "flake8.formatting.default:Pylint", "flake8.report"
            ),
        ),
        finder.Plugin(
            "flake8-foo",
            "1.2.3",
            importlib_metadata.EntryPoint(
                "Q", "flake8_foo:Plugin", "flake8.extension"
            ),
        ),
        finder.Plugin(
            "flake8-foo",
            "1.2.3",
            importlib_metadata.EntryPoint(
                "foo", "flake8_foo:Formatter", "flake8.report"
            ),
        ),
        finder.Plugin(
            "local",
            "local",
            importlib_metadata.EntryPoint("X", "mod:attr", "flake8.extension"),
        ),
        finder.Plugin(
            "local",
            "local",
            importlib_metadata.EntryPoint(
                "Y", "mod2:attr", "flake8.extension"
            ),
        ),
        finder.Plugin(
            "local",
            "local",
            importlib_metadata.EntryPoint("Z", "mod3:attr", "flake8.report"),
        ),
        finder.Plugin(
            "pycodestyle",
            "9000.2.0",
            importlib_metadata.EntryPoint(
                "pycodestyle.bare_except",
                "pycodestyle:bare_except",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "pycodestyle",
            "9000.2.0",
            importlib_metadata.EntryPoint(
                "pycodestyle.blank_lines",
                "pycodestyle:blank_lines",
                "flake8.extension",
            ),
        ),
        finder.Plugin(
            "pyflakes",
            "9000.1.0",
            importlib_metadata.EntryPoint(
                "F",
                "flake8.plugins.pyflakes:FlakesChecker",
                "flake8.extension",
            ),
        ),
    ]


def test_find_local_plugin_paths_missing(tmp_path):
    cfg = configparser.RawConfigParser()
    assert finder.find_local_plugin_paths(cfg, str(tmp_path)) == []


def test_find_local_plugin_paths(tmp_path):
    cfg = configparser.RawConfigParser()
    cfg.add_section("flake8:local-plugins")
    cfg.set("flake8:local-plugins", "paths", "./a, ./b")
    ret = finder.find_local_plugin_paths(cfg, str(tmp_path))

    assert ret == [str(tmp_path.joinpath("a")), str(tmp_path.joinpath("b"))]


def test_parameters_for_class_plugin():
    """Verify that we can retrieve the parameters for a class plugin."""

    class FakeCheck:
        def __init__(self, tree):
            raise NotImplementedError

    assert finder._parameters_for(FakeCheck) == {"tree": True}


def test_parameters_for_function_plugin():
    """Verify that we retrieve the parameters for a function plugin."""

    def fake_plugin(physical_line, self, tree, optional=None):
        raise NotImplementedError

    assert finder._parameters_for(fake_plugin) == {
        "physical_line": True,
        "self": True,
        "tree": True,
        "optional": False,
    }


def test_load_plugin_import_error():
    plugin = _plugin(ep=_ep(value="dne:dne"))

    with pytest.raises(FailedToLoadPlugin) as excinfo:
        finder._load_plugin(plugin)

    pkg, e = excinfo.value.args
    assert pkg == "local"
    assert isinstance(e, ModuleNotFoundError)


def test_load_plugin_not_callable():
    plugin = _plugin(ep=_ep(value="os:curdir"))

    with pytest.raises(FailedToLoadPlugin) as excinfo:
        finder._load_plugin(plugin)

    pkg, e = excinfo.value.args
    assert pkg == "local"
    assert isinstance(e, TypeError)
    assert e.args == ("expected loaded plugin to be callable",)


def test_load_plugin_ok():
    plugin = _plugin(ep=_ep(value="flake8.plugins.pyflakes:FlakesChecker"))

    loaded = finder._load_plugin(plugin)

    assert loaded == finder.LoadedPlugin(
        plugin,
        FlakesChecker,
        {"tree": True, "file_tokens": True, "filename": True},
    )


@pytest.fixture
def reset_sys():
    orig_path = sys.path[:]
    orig_modules = sys.modules.copy()
    yield
    sys.path[:] = orig_path
    sys.modules.clear()
    sys.modules.update(orig_modules)


@pytest.mark.usefixtures("reset_sys")
def test_import_plugins_extends_sys_path():
    plugin = _plugin(ep=_ep(value="aplugin:ExtensionTestPlugin2"))

    ret = finder._import_plugins([plugin], ["tests/integration/subdir"])

    import aplugin

    assert ret == [
        finder.LoadedPlugin(
            plugin,
            aplugin.ExtensionTestPlugin2,
            {"tree": True},
        ),
    ]


def test_classify_plugins():
    report_plugin = _loaded(
        plugin=_plugin(ep=_ep(name="R", group="flake8.report"))
    )
    tree_plugin = _loaded(parameters={"tree": True})
    logical_line_plugin = _loaded(parameters={"logical_line": True})
    physical_line_plugin = _loaded(parameters={"physical_line": True})

    classified = finder._classify_plugins(
        [
            report_plugin,
            tree_plugin,
            logical_line_plugin,
            physical_line_plugin,
        ],
        set(),
    )

    assert classified == finder.Plugins(
        checkers=finder.Checkers(
            tree=[tree_plugin],
            logical_line=[logical_line_plugin],
            physical_line=[physical_line_plugin],
        ),
        reporters={"R": report_plugin},
        disabled=[],
    )


def test_classify_plugins_enable_a_disabled_plugin():
    obj = mock.Mock(off_by_default=True)
    plugin = _plugin(ep=_ep(name="ABC"))
    loaded = _loaded(plugin=plugin, parameters={"tree": True}, obj=obj)

    classified_normal = finder._classify_plugins([loaded], set())
    classified_enabled = finder._classify_plugins([loaded], {"ABC"})

    assert classified_normal == finder.Plugins(
        checkers=finder.Checkers([], [], []),
        reporters={},
        disabled=[loaded],
    )
    assert classified_enabled == finder.Plugins(
        checkers=finder.Checkers([loaded], [], []),
        reporters={},
        disabled=[],
    )


@pytest.mark.usefixtures("reset_sys")
def test_load_plugins():
    plugin = _plugin(ep=_ep(value="aplugin:ExtensionTestPlugin2"))

    ret = finder.load_plugins([plugin], ["tests/integration/subdir"], set())

    import aplugin

    assert ret == finder.Plugins(
        checkers=finder.Checkers(
            tree=[
                finder.LoadedPlugin(
                    plugin,
                    aplugin.ExtensionTestPlugin2,
                    {"tree": True},
                ),
            ],
            logical_line=[],
            physical_line=[],
        ),
        reporters={},
        disabled=[],
    )
