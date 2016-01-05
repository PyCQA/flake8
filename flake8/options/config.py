import logging
import os.path
import sys

if sys.version_info < (3, 0):
    import ConfigParser as configparser
else:
    import configparser

from . import utils

LOG = logging.getLogger(__name__)


class ConfigFileFinder(object):
    PROJECT_FILENAMES = ('setup.cfg', 'tox.ini')

    def __init__(self, program_name, args):
        # Platform specific settings
        self.is_windows = sys.platform == 'win32'
        self.xdg_home = os.environ.get('XDG_CONFIG_HOME',
                                       os.path.expanduser('~/.config'))

        # Look for '.<program_name>' files
        self.program_config = '.' + program_name
        self.program_name = program_name

        # List of filenames to find in the local/project directory
        self.project_filenames = ('setup.cfg', 'tox.ini', self.program_config)
        # List of filenames to find "globally"
        self.global_filenames = (self.program_config,)

        self.local_directory = os.curdir

        if not args:
            args = ['.']
        self.parent = self.tail = os.path.abspath(os.path.commonprefix(args))

    @staticmethod
    def _read_config(files):
        config = configparser.RawConfigParser()
        found_files = config.read(files)
        return (config, found_files)

    def generate_possible_local_config_files(self):
        tail = self.tail
        parent = self.parent
        while tail:
            for project_filename in self.project_filenames:
                filename = os.path.abspath(os.path.join(parent,
                                                        project_filename))
                yield filename
            (parent, tail) = os.path.split(parent)

    def local_config_files(self):
        return [
            filename
            for filename in self.generate_possible_local_config_files()
            if os.path.exists(filename)
        ]

    def local_configs(self):
        config, found_files = self._read_config(self.local_config_files())
        if found_files:
            LOG.debug('Found local configuration files: %s', found_files)
        return config

    def user_config_file(self):
        if self.is_windows:
            return os.path.expanduser('~\\' + self.program_config)
        return os.path.join(self.xdg_home, self.program_name)

    def user_config(self):
        config, found_files = self._read_config(self.user_config_file())
        if found_files:
            LOG.debug('Found user configuration files: %s', found_files)
        return config


class MergedConfigParser(object):
    GETINT_METHODS = set(['int', 'count'])
    GETBOOL_METHODS = set(['store_true', 'store_false'])

    def __init__(self, option_manager, args=None):
        self.option_manager = option_manager
        self.program_name = option_manager.program_name
        self.args = args
        self.config_finder = ConfigFileFinder(self.program_name, self.args)
        self.config_options = option_manager.config_options_dict

    def _parse_config(self, config_parser):
        config = self.config_finder.local_configs()
        if not config.has_section(self.program_name):
            LOG.debug('Local configuration files have no %s section',
                      self.program_name)
            return {}

        config_dict = {}
        for option_name in config_parser.options(self.program_name):
            if option_name not in self.config_options:
                LOG.debug('Option "%s" is not registered. Ignoring.',
                          option_name)
                continue
            option = self.config_options[option_name]

            # Use the appropriate method to parse the config value
            method = config.get
            if option.type in self.GETINT_METHODS:
                method = config.getint
            elif option.action in self.GETBOOL_METHODS:
                method = config.getboolean

            value = method(self.program_name, option_name)
            LOG.debug('Option "%s" returned value: %r', option_name, value)

            final_value = value
            if option.comma_separated_list:
                final_value = utils.parse_comma_separated_list(value)

            config_dict[option_name] = final_value

    def is_configured_by(self, config):
        """Check if the specified config parser has an appropriate section."""
        return config.has_section(self.program_name)

    def parse_local_config(self):
        """Parse and return the local configuration files."""
        config = self.config_finder.local_configs()
        if not self.is_configured_by(config):
            LOG.debug('Local configuration files have no %s section',
                      self.program_name)
            return

        LOG.debug('Parsing local configuration files.')
        return self._parse_config(config)

    def parse_user_config(self):
        """Parse and return the user configuration files."""
        config = self.config_finder.user_config()
        if not self.is_configured_by(config):
            LOG.debug('User configuration files have no %s section',
                      self.program_name)
            return

        LOG.debug('Parsing user configuration files.')
        return self._parse_config(config)

    def parse(self):
        """Parse and return the local and user config files.

        First this copies over the parsed local configuration and then
        iterates over the options in the user configuration and sets them if
        they were not set by the local configuration file.
        """
        user_config = self.parse_user_config()
        config = self.parse_local_config()

        for option, value in user_config.items():
            config.setdefault(option, value)

        return config
