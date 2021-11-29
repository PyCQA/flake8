import configparser

import pytest

from flake8.main.options import register_default_options
from flake8.options import config
from flake8.options.manager import OptionManager


def test_config_not_found_returns_none(tmp_path):
    config.ADDITIONAL_LOCATIONS = []
    config.ADDITIONAL_CANDIDATES = []
    assert config._find_config_file(str(tmp_path)) is None


def test_config_file_without_section_is_not_considered(tmp_path):
    tmp_path.joinpath("setup.cfg").touch()

    assert config._find_config_file(str(tmp_path)) is None


def test_config_file_with_parse_error_is_not_considered(tmp_path, caplog):
    tmp_path.joinpath("setup.cfg").write_text("[error")

    assert config._find_config_file(str(tmp_path)) is None

    assert len(caplog.record_tuples) == 1
    ((mod, level, msg),) = caplog.record_tuples
    assert (mod, level) == ("flake8.options.config", 30)
    assert msg.startswith("ignoring unparseable config ")


def test_config_file_with_encoding_error_is_not_considered(tmp_path, caplog):
    tmp_path.joinpath("setup.cfg").write_bytes(b"\xa0\xef\xfe\x12")

    assert config._find_config_file(str(tmp_path)) is None

    assert len(caplog.record_tuples) == 1
    ((mod, level, msg),) = caplog.record_tuples
    assert (mod, level) == ("flake8.options.config", 30)
    assert msg.startswith("ignoring unparseable config ")


@pytest.mark.parametrize("cfg_name", ("setup.cfg", "tox.ini", ".flake8"))
def test_find_config_file_exists_at_path(tmp_path, cfg_name):
    expected = tmp_path.joinpath(cfg_name)
    expected.write_text("[flake8]")

    assert config._find_config_file(str(tmp_path)) == str(expected)


@pytest.mark.parametrize("section", ("flake8", "flake8:local-plugins"))
def test_find_config_either_section(tmp_path, section):
    expected = tmp_path.joinpath("setup.cfg")
    expected.write_text(f"[{section}]")

    assert config._find_config_file(str(tmp_path)) == str(expected)


def test_find_config_searches_upwards(tmp_path):
    subdir = tmp_path.joinpath("d")
    subdir.mkdir()

    expected = tmp_path.joinpath("setup.cfg")
    expected.write_text("[flake8]")

    assert config._find_config_file(str(subdir)) == str(expected)


def test_load_config_config_specified_skips_discovery(tmpdir):
    tmpdir.join("setup.cfg").write("[flake8]\nindent-size=2\n")
    custom_cfg = tmpdir.join("custom.cfg")
    custom_cfg.write("[flake8]\nindent-size=8\n")

    with tmpdir.as_cwd():
        cfg, cfg_dir = config.load_config(str(custom_cfg), [], isolated=False)

    assert cfg.get("flake8", "indent-size") == "8"
    assert cfg_dir == str(tmpdir)


def test_load_config_no_config_file_does_discovery(tmpdir):
    tmpdir.join("setup.cfg").write("[flake8]\nindent-size=2\n")

    with tmpdir.as_cwd():
        cfg, cfg_dir = config.load_config(None, [], isolated=False)

    assert cfg.get("flake8", "indent-size") == "2"
    assert cfg_dir == str(tmpdir)


def test_load_config_no_config_found_sets_cfg_dir_to_pwd(tmpdir):
    with tmpdir.as_cwd():
        cfg, cfg_dir = config.load_config(None, [], isolated=False)

    assert cfg.sections() == []
    assert cfg_dir == str(tmpdir)


def test_load_config_isolated_ignores_configuration(tmpdir):
    tmpdir.join("setup.cfg").write("[flake8]\nindent-size=2\n")

    with tmpdir.as_cwd():
        cfg, cfg_dir = config.load_config(None, [], isolated=True)

    assert cfg.sections() == []
    assert cfg_dir == str(tmpdir)


def test_load_config_append_config(tmpdir):
    tmpdir.join("setup.cfg").write("[flake8]\nindent-size=2\n")
    other = tmpdir.join("other.cfg")
    other.write("[flake8]\nindent-size=8\n")

    with tmpdir.as_cwd():
        cfg, cfg_dir = config.load_config(None, [str(other)], isolated=False)

    assert cfg.get("flake8", "indent-size") == "8"
    assert cfg_dir == str(tmpdir)


@pytest.fixture
def opt_manager():
    ret = OptionManager(prog="flake8", version="123")
    register_default_options(ret)
    return ret


def test_parse_config_no_values(tmp_path, opt_manager):
    cfg = configparser.RawConfigParser()
    ret = config.parse_config(opt_manager, cfg, tmp_path)
    assert ret == {}


def test_parse_config_typed_values(tmp_path, opt_manager):
    cfg = configparser.RawConfigParser()
    cfg.add_section("flake8")
    cfg.set("flake8", "indent_size", "2")
    cfg.set("flake8", "hang_closing", "true")
    # test normalizing dashed-options
    cfg.set("flake8", "extend-exclude", "d/1,d/2")

    ret = config.parse_config(opt_manager, cfg, str(tmp_path))
    assert ret == {
        "indent_size": 2,
        "hang_closing": True,
        "extend_exclude": [
            str(tmp_path.joinpath("d/1")),
            str(tmp_path.joinpath("d/2")),
        ],
    }


def test_parse_config_ignores_unknowns(tmp_path, opt_manager, caplog):
    cfg = configparser.RawConfigParser()
    cfg.add_section("flake8")
    cfg.set("flake8", "wat", "wat")

    ret = config.parse_config(opt_manager, cfg, str(tmp_path))
    assert ret == {}

    assert caplog.record_tuples == [
        (
            "flake8.options.config",
            10,
            'Option "wat" is not registered. Ignoring.',
        )
    ]
