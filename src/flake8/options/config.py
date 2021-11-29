"""Config handling logic for Flake8."""
import configparser
import logging
import os.path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from flake8.options.manager import OptionManager

LOG = logging.getLogger(__name__)
DEFAULT_CANDIDATES = ["setup.cfg", "tox.ini", ".flake8"]
ADDITIONAL_CANDIDATES = ["flake8"]
ADDITIONAL_LOCATIONS = [
    os.path.expanduser(r"~"),
    os.path.expanduser(r"~/.config"),
]


def _is_config(path: str) -> bool:
    cfg = configparser.RawConfigParser()
    try:
        cfg.read(path)
    except (UnicodeDecodeError, configparser.ParsingError) as e:
        LOG.warning("ignoring unparseable config %s: %s", path, e)
    else:
        # only consider it a config if it contains flake8 sections
        if "flake8" in cfg or "flake8:local-plugins" in cfg:
            return True
    return False


def _find_config_file(path: str) -> Optional[str]:
    while True:
        for candidate in DEFAULT_CANDIDATES:
            cfg_path = os.path.join(path, candidate)
            if _is_config(cfg_path):
                return cfg_path

        new_path = os.path.dirname(path)
        if new_path == path:
            break
        else:
            path = new_path

    # try some additional locations with additional candidate names
    candidates = DEFAULT_CANDIDATES + ADDITIONAL_CANDIDATES
    for location in ADDITIONAL_LOCATIONS:
        for candidate in candidates:
            cfg_path = os.path.join(location, candidate)
            if _is_config(cfg_path):
                return cfg_path

    # did not find any configuration file
    return None


def load_config(
    config: Optional[str],
    extra: List[str],
    *,
    isolated: bool = False,
) -> Tuple[configparser.RawConfigParser, str]:
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
        cfg.read(config)
        cfg_dir = os.path.dirname(config)
    else:
        cfg_dir = pwd

    # TODO: remove this and replace it with configuration modifying plugins
    # read the additional configs afterwards
    for filename in extra:
        cfg.read(filename)

    return cfg, cfg_dir


def parse_config(
    option_manager: OptionManager,
    cfg: configparser.RawConfigParser,
    cfg_dir: str,
) -> Dict[str, Any]:
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
