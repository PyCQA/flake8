"""Aggregation function for CLI specified options and config file options.

This holds the logic that uses the collected and merged config files and
applies the user-specified command-line configuration on top of it.
"""
import argparse
import configparser
import logging
from typing import Optional
from typing import Sequence

from flake8.options import config
from flake8.options.manager import OptionManager

LOG = logging.getLogger(__name__)


def aggregate_options(
    manager: OptionManager,
    cfg: configparser.RawConfigParser,
    cfg_dir: str,
    argv: Optional[Sequence[str]],
) -> argparse.Namespace:
    """Aggregate and merge CLI and config file options."""
    # Get defaults from the option parser
    default_values = manager.parse_args([])

    # Get the parsed config
    parsed_config = config.parse_config(manager, cfg, cfg_dir)

    # Extend the default ignore value with the extended default ignore list,
    # registered by plugins.
    extended_default_ignore = manager.extended_default_ignore.copy()
    # Let's store our extended default ignore for use by the decision engine
    default_values.extended_default_ignore = (
        manager.extended_default_ignore.copy()
    )
    LOG.debug(
        "Extended default ignore list: %s", list(extended_default_ignore)
    )
    extended_default_ignore.update(default_values.ignore)
    default_values.ignore = list(extended_default_ignore)
    LOG.debug("Merged default ignore list: %s", default_values.ignore)

    extended_default_select = manager.extended_default_select.copy()
    LOG.debug(
        "Extended default select list: %s", list(extended_default_select)
    )
    default_values.extended_default_select = extended_default_select

    # Merge values parsed from config onto the default values returned
    for config_name, value in parsed_config.items():
        dest_name = config_name
        # If the config name is somehow different from the destination name,
        # fetch the destination name from our Option
        if not hasattr(default_values, config_name):
            dest_val = manager.config_options_dict[config_name].dest
            assert isinstance(dest_val, str)
            dest_name = dest_val

        LOG.debug(
            'Overriding default value of (%s) for "%s" with (%s)',
            getattr(default_values, dest_name, None),
            dest_name,
            value,
        )
        # Override the default values with the config values
        setattr(default_values, dest_name, value)

    # Finally parse the command-line options
    return manager.parse_args(argv, default_values)
