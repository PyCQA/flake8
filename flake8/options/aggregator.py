"""Aggregation function for CLI specified options and config file options.

This holds the logic that uses the collected and merged config files and
applies the user-specified command-line configuration on top of it.
"""
import logging

from flake8.options import config
from flake8 import utils

LOG = logging.getLogger(__name__)


def aggregate_options(manager, arglist=None, values=None):
    """Function that aggregates the CLI and Config options."""
    # Get defaults from the option parser
    default_values, _ = manager.parse_args([], values=values)
    # Get original CLI values so we can find additional config file paths and
    # see if --config was specified.
    original_values, original_args = manager.parse_args(arglist)
    extra_config_files = utils.normalize_paths(original_values.append_config)

    # Make our new configuration file mergerator
    config_parser = config.MergedConfigParser(
        option_manager=manager,
        extra_config_files=extra_config_files,
        args=original_args,
    )

    # Get the parsed config
    parsed_config = config_parser.parse(original_values.config,
                                        original_values.isolated)

    # Merge values parsed from config onto the default values returned
    for config_name, value in parsed_config.items():
        dest_name = config_name
        # If the config name is somehow different from the destination name,
        # fetch the destination name from our Option
        if not hasattr(default_values, config_name):
            dest_name = config_parser.config_options[config_name].dest

        LOG.debug('Overriding default value of (%s) for "%s" with (%s)',
                  getattr(default_values, dest_name, None),
                  dest_name,
                  value)
        # Override the default values with the config values
        setattr(default_values, dest_name, value)

    # Finally parse the command-line options
    final_values, args = manager.parse_args(arglist, default_values)
    return final_values, args
