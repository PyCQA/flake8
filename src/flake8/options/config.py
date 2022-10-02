"""Config handling logic for Flake8."""
from __future__ import annotations

import configparser
import logging
import os.path
from typing import Any
from typing import Generator

from flake8 import exceptions
from flake8.options.manager import OptionManager

LOG = logging.getLogger(__name__)


def _stat_key(s: str) -> tuple[int, int]:
    # same as what's used by samefile / samestat
    st = os.stat(s)
    return st.st_ino, st.st_dev


def _walk_up_directories_to_root_or_home(
    path: str,
) -> Generator[str, None, None]:
    """Walk upwards from the given directory.

    Walk upwards from the given directory until either the root or the home
    directory is reached. Do not include the root or home directory.

    :param path:
        The starting path. The generator will yield this path, followed by its
        parent, followed by the parent of its parent, and so forth.
    :returns:
        The directory paths, as strings, from bottom to top.
    """
    # on windows if the homedir isn't detected this returns back `~`
    home = os.path.expanduser("~")
    try:
        home_stat = _stat_key(home) if home != "~" else None
    except OSError:  # FileNotFoundError / PermissionError / etc.
        home_stat = None

    dir_stat = _stat_key(path)
    while True:
        new_path = os.path.dirname(path)
        new_dir_stat = _stat_key(new_path)
        if new_dir_stat == dir_stat or new_dir_stat == home_stat:
            break
        else:
            path = new_path
            dir_stat = new_dir_stat
            yield path


def _find_config_file(path: str) -> str | None:
    for path in _walk_up_directories_to_root_or_home(path):
        for candidate in ("setup.cfg", "tox.ini", ".flake8"):
            cfg = configparser.RawConfigParser()
            cfg_path = os.path.join(path, candidate)
            try:
                cfg.read(cfg_path, encoding="UTF-8")
            except (UnicodeDecodeError, configparser.ParsingError) as e:
                LOG.warning("ignoring unparseable config %s: %s", cfg_path, e)
            else:
                # only consider it a config if it contains flake8 sections
                if "flake8" in cfg or "flake8:local-plugins" in cfg:
                    return cfg_path

    # did not find any configuration file
    return None


def load_config(
    config: str | None,
    extra: list[str],
    *,
    isolated: bool = False,
) -> tuple[configparser.RawConfigParser, str]:
    """Load the configuration given the user options.

    - in ``isolated`` mode, return an empty configuration
    - if a config file is given in ``config`` use that, otherwise attempt to
      discover a configuration using ``tox.ini`` / ``setup.cfg`` / ``.flake8``
    - finally, load any ``extra`` configuration files
    """
    pwd = os.path.abspath(".")

    if isolated:
        return configparser.RawConfigParser(), pwd

    if config is None:
        config = _find_config_file(pwd)

    cfg = configparser.RawConfigParser()
    if config is not None:
        if not cfg.read(config, encoding="UTF-8"):
            raise exceptions.ExecutionError(
                f"The specified config file does not exist: {config}"
            )
        cfg_dir = os.path.dirname(config)
    else:
        cfg_dir = pwd

    # TODO: remove this and replace it with configuration modifying plugins
    # read the additional configs afterwards
    for filename in extra:
        cfg.read(filename, encoding="UTF-8")

    return cfg, cfg_dir


def parse_config(
    option_manager: OptionManager,
    cfg: configparser.RawConfigParser,
    cfg_dir: str,
) -> dict[str, Any]:
    """Parse and normalize the typed configuration options."""
    if "flake8" not in cfg:
        return {}

    config_dict = {}

    for option_name in cfg["flake8"]:
        option = option_manager.config_options_dict.get(option_name)
        if option is None:
            LOG.debug('Option "%s" is not registered. Ignoring.', option_name)
            continue

        # Use the appropriate method to parse the config value
        value: Any
        if option.type is int or option.action == "count":
            value = cfg.getint("flake8", option_name)
        elif option.action in {"store_true", "store_false"}:
            value = cfg.getboolean("flake8", option_name)
        else:
            value = cfg.get("flake8", option_name)

        LOG.debug('Option "%s" returned value: %r', option_name, value)

        final_value = option.normalize(value, cfg_dir)
        assert option.config_name is not None
        config_dict[option.config_name] = final_value

    return config_dict
