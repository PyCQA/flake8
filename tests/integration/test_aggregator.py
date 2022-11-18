"""Test aggregation of config files and command-line options."""
from __future__ import annotations

import os

import pytest

from flake8.main import options
from flake8.options import aggregator
from flake8.options import config
from flake8.options import manager


@pytest.fixture
def optmanager():
    """Create a new OptionManager."""
    option_manager = manager.OptionManager(
        version="3.0.0",
        plugin_versions="",
        parents=[],
        formatter_names=[],
    )
    options.register_default_options(option_manager)
    return option_manager


@pytest.fixture
def flake8_config(tmp_path):
    cfg_s = """\
[flake8]
ignore =
    E123,
    W234,
    E111
exclude =
    foo/,
    bar/,
    bogus/
quiet = 1
"""
    cfg = tmp_path.joinpath("tox.ini")
    cfg.write_text(cfg_s)
    return str(cfg)


def test_aggregate_options_with_config(optmanager, flake8_config):
    """Verify we aggregate options and config values appropriately."""
    arguments = [
        "flake8",
        "--select",
        "E11,E34,E402,W,F",
        "--exclude",
        "tests/*",
    ]
    cfg, cfg_dir = config.load_config(flake8_config, [])
    options = aggregator.aggregate_options(
        optmanager,
        cfg,
        cfg_dir,
        arguments,
    )

    assert options.select == ["E11", "E34", "E402", "W", "F"]
    assert options.ignore == ["E123", "W234", "E111"]
    assert options.exclude == [os.path.abspath("tests/*")]


def test_aggregate_options_when_isolated(optmanager, flake8_config):
    """Verify we aggregate options and config values appropriately."""
    arguments = [
        "flake8",
        "--select",
        "E11,E34,E402,W,F",
        "--exclude",
        "tests/*",
    ]
    cfg, cfg_dir = config.load_config(flake8_config, [], isolated=True)
    optmanager.extend_default_ignore(["E8"])
    options = aggregator.aggregate_options(optmanager, cfg, cfg_dir, arguments)

    assert options.select == ["E11", "E34", "E402", "W", "F"]
    assert options.ignore is None
    assert options.exclude == [os.path.abspath("tests/*")]
