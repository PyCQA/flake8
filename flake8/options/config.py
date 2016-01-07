import logging
import os.path
import sys

if sys.version_info < (3, 0):
    import ConfigParser as configparser
else:
    import configparser

from . import utils

LOG = logging.getLogger(__name__)

__all__('ConfigFileFinder', 'MergedConfigParser')


class ConfigFileFinder(object):
    PROJECT_FILENAMES = ('setup.cfg', 'tox.ini')

    def __init__(self, program_name, args, extra_config_files):
        # The values of --append-config from the CLI
        self.extra_config_files = extra_config_files

        # Platform specific settings
        self.is_windows = sys.platform == 'win32'
        self.xdg_home = os.environ.get('XDG_CONFIG_HOME',
                                       os.path.expanduser('~/.config'))

        # Look for '.<program_name>' files
        self.program_config = '.' + program_name
        self.program_name = program_name

        # List of filenames to find in the local/project directory
        self.project_filenames = ('setup.cfg', 'tox.ini', self.program_config)

        self.local_directory = os.curdir

        if not args:
            args = ['.']
        self.parent = self.tail = os.path.abspath(os.path.commonprefix(args))

    @staticmethod
    def _read_config(files):
        config = configparser.RawConfigParser()
        found_files = config.read(files)
        return (config, found_files)

    def cli_config(self, files):
        config, found_files = self._read_config(files)
        if found_files:
            LOG.debug('Found cli configuration files: %s', found_files)
        return config

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
        ] + self.extra_config_files

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

    def __init__(self, option_manager, extra_config_files=None, args=None):
        # Our instance of flake8.options.manager.OptionManager
        self.option_manager = option_manager
        # The prog value for the cli parser
        self.program_name = option_manager.program_name
        # Parsed extra arguments
        self.args = args
        # Our instance of our ConfigFileFinder
        self.config_finder = ConfigFileFinder(self.program_name, self.args)
        # Mapping of configuration option names to
        # flake8.options.manager.Option instances
        self.config_options = option_manager.config_options_dict
        self.extra_config_files = extra_config_files or []

    @staticmethod
    def _normalize_value(option, value):
        if option.normalize_paths:
            final_value = utils.normalize_paths(value)
        elif option.comma_separated_list:
            final_value = utils.parse_comma_separated_list(value)
        else:
            final_value = value
        LOG.debug('%r has been normalized to %r for option "%s"',
                  value, final_value, option.config_name)
        return final_value

    def _parse_config(self, config_parser):
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

            final_value = self._normalize_value(value)
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
            return {}

        LOG.debug('Parsing local configuration files.')
        return self._parse_config(config)

    def parse_user_config(self):
        """Parse and return the user configuration files."""
        config = self.config_finder.user_config()
        if not self.is_configured_by(config):
            LOG.debug('User configuration files have no %s section',
                      self.program_name)
            return {}

        LOG.debug('Parsing user configuration files.')
        return self._parse_config(config)

    def parse_cli_config(self, config_path):
        """Parse and return the file specified by --config."""
        config = self.config_finder.cli_config(config_path)
        if not self.is_configured_by(config):
            LOG.debug('CLI configuration files have no %s section',
                      self.program_name)
            return {}

        LOG.debug('Parsing CLI configuration files.')
        return self._parse_config(config)

    def parse(self, cli_config=None, isolated=False):
        """Parse and return the local and user config files.

        First this copies over the parsed local configuration and then
        iterates over the options in the user configuration and sets them if
        they were not set by the local configuration file.

        :param str cli_config:
            Value of --config when specified at the command-line. Overrides
            all other config files.
        :param bool isolated:
            Determines if we should parse configuration files at all or not.
            If running in isolated mode, we ignore all configuration files
        :returns:
            Dictionary of parsed configuration options
        :rtype:
            dict
        """
        if isolated:
            LOG.debug('Refusing to parse configuration files due to user-'
                      'requested isolation')
            return {}

        if cli_config:
            LOG.debug('Ignoring user and locally found configuration files. '
                      'Reading only configuration from "%s" specified via '
                      '--config by the user', cli_config)
            return self.parse_cli_config(cli_config)

        user_config = self.parse_user_config()
        config = self.parse_local_config()

        for option, value in user_config.items():
            config.setdefault(option, value)

        return config
