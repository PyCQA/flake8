"""Config handling logic for Flake8."""
import collections
import configparser
import logging
import os.path
import sys
from typing import Dict, List, Optional, Tuple

from flake8 import utils

LOG = logging.getLogger(__name__)

__all__ = ("ConfigFileFinder", "MergedConfigParser")


class ConfigFileFinder(object):
    """Encapsulate the logic for finding and reading config files."""

    def __init__(
        self,
        program_name,
        extra_config_files,
        config_file=None,
        ignore_config_files=False,
    ):
        # type: (str, List[str], Optional[str], bool) -> None
        """Initialize object to find config files.

        :param str program_name:
            Name of the current program (e.g., flake8).
        :param list extra_config_files:
            Extra configuration files specified by the user to read.
        :param str config_file:
            Configuration file override to only read configuraiton from.
        :param bool ignore_config_files:
            Determine whether to ignore configuration files or not.
        """
        # The values of --append-config from the CLI
        extra_config_files = extra_config_files or []
        self.extra_config_files = utils.normalize_paths(extra_config_files)

        # The value of --config from the CLI.
        self.config_file = config_file

        # The value of --isolated from the CLI.
        self.ignore_config_files = ignore_config_files

        # Platform specific settings
        self.is_windows = sys.platform == "win32"
        self.xdg_home = os.environ.get(
            "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
        )

        # Look for '.<program_name>' files
        self.program_config = "." + program_name
        self.program_name = program_name

        # List of filenames to find in the local/project directory
        self.project_filenames = ("setup.cfg", "tox.ini", self.program_config)

        self.local_directory = os.path.abspath(os.curdir)

        # caches to avoid double-reading config files
        self._local_configs = None
        self._local_found_files = []  # type: List[str]
        self._user_config = None
        # fmt: off
        self._cli_configs = {}  # type: Dict[str, configparser.RawConfigParser]
        # fmt: on

    @staticmethod
    def _read_config(*files):
        # type: (*str) -> Tuple[configparser.RawConfigParser, List[str]]
        config = configparser.RawConfigParser()

        found_files = []
        for filename in files:
            try:
                found_files.extend(config.read(filename))
            except UnicodeDecodeError:
                LOG.exception(
                    "There was an error decoding a config file."
                    "The file with a problem was %s.",
                    filename,
                )
            except configparser.ParsingError:
                LOG.exception(
                    "There was an error trying to parse a config "
                    "file. The file with a problem was %s.",
                    filename,
                )
        return (config, found_files)

    def cli_config(self, files):
        # type: (str) -> configparser.RawConfigParser
        """Read and parse the config file specified on the command-line."""
        if files not in self._cli_configs:
            config, found_files = self._read_config(files)
            if found_files:
                LOG.debug("Found cli configuration files: %s", found_files)
            self._cli_configs[files] = config
        return self._cli_configs[files]

    def generate_possible_local_files(self):
        """Find and generate all local config files."""
        parent = tail = os.getcwd()
        found_config_files = False
        while tail and not found_config_files:
            for project_filename in self.project_filenames:
                filename = os.path.abspath(
                    os.path.join(parent, project_filename)
                )
                if os.path.exists(filename):
                    yield filename
                    found_config_files = True
                    self.local_directory = parent
            (parent, tail) = os.path.split(parent)

    def local_config_files(self):
        """Find all local config files which actually exist.

        Filter results from
        :meth:`~ConfigFileFinder.generate_possible_local_files` based
        on whether the filename exists or not.

        :returns:
            List of files that exist that are local project config files with
            extra config files appended to that list (which also exist).
        :rtype:
            [str]
        """
        exists = os.path.exists
        return [
            filename for filename in self.generate_possible_local_files()
        ] + [f for f in self.extra_config_files if exists(f)]

    def local_configs_with_files(self):
        """Parse all local config files into one config object.

        Return (config, found_config_files) tuple.
        """
        if self._local_configs is None:
            config, found_files = self._read_config(
                *self.local_config_files()
            )
            if found_files:
                LOG.debug("Found local configuration files: %s", found_files)
            self._local_configs = config
            self._local_found_files = found_files
        return (self._local_configs, self._local_found_files)

    def local_configs(self):
        """Parse all local config files into one config object."""
        return self.local_configs_with_files()[0]

    def user_config_file(self):
        """Find the user-level config file."""
        if self.is_windows:
            return os.path.expanduser("~\\" + self.program_config)
        return os.path.join(self.xdg_home, self.program_name)

    def user_config(self):
        """Parse the user config file into a config object."""
        if self._user_config is None:
            config, found_files = self._read_config(self.user_config_file())
            if found_files:
                LOG.debug("Found user configuration files: %s", found_files)
            self._user_config = config
        return self._user_config


class MergedConfigParser(object):
    """Encapsulate merging different types of configuration files.

    This parses out the options registered that were specified in the
    configuration files, handles extra configuration files, and returns
    dictionaries with the parsed values.
    """

    #: Set of actions that should use the
    #: :meth:`~configparser.RawConfigParser.getbool` method.
    GETBOOL_ACTIONS = {"store_true", "store_false"}

    def __init__(self, option_manager, config_finder):
        """Initialize the MergedConfigParser instance.

        :param flake8.options.manager.OptionManager option_manager:
            Initialized OptionManager.
        :param flake8.options.config.ConfigFileFinder config_finder:
            Initialized ConfigFileFinder.
        """
        #: Our instance of flake8.options.manager.OptionManager
        self.option_manager = option_manager
        #: The prog value for the cli parser
        self.program_name = option_manager.program_name
        #: Mapping of configuration option names to
        #: :class:`~flake8.options.manager.Option` instances
        self.config_options = option_manager.config_options_dict
        #: Our instance of our :class:`~ConfigFileFinder`
        self.config_finder = config_finder

    def _normalize_value(self, option, value):
        final_value = option.normalize(
            value, self.config_finder.local_directory
        )
        LOG.debug(
            '%r has been normalized to %r for option "%s"',
            value,
            final_value,
            option.config_name,
        )
        return final_value

    def _parse_config(self, config_parser):
        config_dict = {}
        for option_name in config_parser.options(self.program_name):
            if option_name not in self.config_options:
                LOG.debug(
                    'Option "%s" is not registered. Ignoring.', option_name
                )
                continue
            option = self.config_options[option_name]

            # Use the appropriate method to parse the config value
            method = config_parser.get
            if option.type is int or option.action == "count":
                method = config_parser.getint
            elif option.action in self.GETBOOL_ACTIONS:
                method = config_parser.getboolean

            value = method(self.program_name, option_name)
            LOG.debug('Option "%s" returned value: %r', option_name, value)

            final_value = self._normalize_value(option, value)
            config_dict[option.config_name] = final_value

        return config_dict

    def is_configured_by(self, config):
        """Check if the specified config parser has an appropriate section."""
        return config.has_section(self.program_name)

    def parse_local_config(self):
        """Parse and return the local configuration files."""
        config = self.config_finder.local_configs()
        if not self.is_configured_by(config):
            LOG.debug(
                "Local configuration files have no %s section",
                self.program_name,
            )
            return {}

        LOG.debug("Parsing local configuration files.")
        return self._parse_config(config)

    def parse_user_config(self):
        """Parse and return the user configuration files."""
        config = self.config_finder.user_config()
        if not self.is_configured_by(config):
            LOG.debug(
                "User configuration files have no %s section",
                self.program_name,
            )
            return {}

        LOG.debug("Parsing user configuration files.")
        return self._parse_config(config)

    def parse_cli_config(self, config_path):
        """Parse and return the file specified by --config."""
        config = self.config_finder.cli_config(config_path)
        if not self.is_configured_by(config):
            LOG.debug(
                "CLI configuration files have no %s section",
                self.program_name,
            )
            return {}

        LOG.debug("Parsing CLI configuration files.")
        return self._parse_config(config)

    def merge_user_and_local_config(self):
        """Merge the parsed user and local configuration files.

        :returns:
            Dictionary of the parsed and merged configuration options.
        :rtype:
            dict
        """
        user_config = self.parse_user_config()
        config = self.parse_local_config()

        for option, value in user_config.items():
            config.setdefault(option, value)

        return config

    def parse(self):
        """Parse and return the local and user config files.

        First this copies over the parsed local configuration and then
        iterates over the options in the user configuration and sets them if
        they were not set by the local configuration file.

        :returns:
            Dictionary of parsed configuration options
        :rtype:
            dict
        """
        if self.config_finder.ignore_config_files:
            LOG.debug(
                "Refusing to parse configuration files due to user-"
                "requested isolation"
            )
            return {}

        if self.config_finder.config_file:
            LOG.debug(
                "Ignoring user and locally found configuration files. "
                'Reading only configuration from "%s" specified via '
                "--config by the user",
                self.config_finder.config_file,
            )
            return self.parse_cli_config(self.config_finder.config_file)

        return self.merge_user_and_local_config()


def get_local_plugins(config_finder):
    """Get local plugins lists from config files.

    :param flake8.options.config.ConfigFileFinder config_finder:
        The config file finder to use.
    :returns:
        LocalPlugins namedtuple containing two lists of plugin strings,
        one for extension (checker) plugins and one for report plugins.
    :rtype:
        flake8.options.config.LocalPlugins
    """
    local_plugins = LocalPlugins(extension=[], report=[], paths=[])
    if config_finder.ignore_config_files:
        LOG.debug(
            "Refusing to look for local plugins in configuration"
            "files due to user-requested isolation"
        )
        return local_plugins

    if config_finder.config_file:
        LOG.debug(
            'Reading local plugins only from "%s" specified via '
            "--config by the user",
            config_finder.config_file,
        )
        config = config_finder.cli_config(config_finder.config_file)
        config_files = [config_finder.config_file]
    else:
        config, config_files = config_finder.local_configs_with_files()

    base_dirs = {os.path.dirname(cf) for cf in config_files}

    section = "%s:local-plugins" % config_finder.program_name
    for plugin_type in ["extension", "report"]:
        if config.has_option(section, plugin_type):
            local_plugins_string = config.get(section, plugin_type).strip()
            plugin_type_list = getattr(local_plugins, plugin_type)
            plugin_type_list.extend(
                utils.parse_comma_separated_list(
                    local_plugins_string, regexp=utils.LOCAL_PLUGIN_LIST_RE
                )
            )
    if config.has_option(section, "paths"):
        raw_paths = utils.parse_comma_separated_list(
            config.get(section, "paths").strip()
        )
        norm_paths = []  # type: List[str]
        for base_dir in base_dirs:
            norm_paths.extend(
                path
                for path in utils.normalize_paths(raw_paths, parent=base_dir)
                if os.path.exists(path)
            )
        local_plugins.paths.extend(norm_paths)
    return local_plugins


LocalPlugins = collections.namedtuple(
    "LocalPlugins", "extension report paths"
)
