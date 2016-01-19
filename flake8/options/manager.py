"""Option handling and Option management logic."""
import logging
import optparse

from flake8 import utils

LOG = logging.getLogger(__name__)


class Option(object):
    """Our wrapper around an optparse.Option object to add features."""

    def __init__(self, short_option_name=None, long_option_name=None,
                 # Options below here are taken from the optparse.Option class
                 action=None, default=None, type=None, dest=None,
                 nargs=None, const=None, choices=None, callback=None,
                 callback_args=None, callback_kwargs=None, help=None,
                 metavar=None,
                 # Options below here are specific to Flake8
                 parse_from_config=False, comma_separated_list=False,
                 normalize_paths=False,
                 ):
        """Initialize an Option instance wrapping optparse.Option.

        The following are all passed directly through to optparse.

        :param str short_option_name:
            The short name of the option (e.g., ``-x``). This will be the
            first argument passed to :class:`~optparse.Option`.
        :param str long_option_name:
            The long name of the option (e.g., ``--xtra-long-option``). This
            will be the second argument passed to :class:`~optparse.Option`.
        :param str action:
            Any action allowed by :mod:`optparse`.
        :param default:
            Default value of the option.
        :param type:
            Any type allowed by :mod:`optparse`.
        :param dest:
            Attribute name to store parsed option value as.
        :param nargs:
            Number of arguments to parse for this option.
        :param const:
            Constant value to store on a common destination. Usually used in
            conjuntion with ``action="store_const"``.
        :param iterable choices:
            Possible values for the option.
        :param callable callback:
            Callback used if the action is ``"callback"``.
        :param iterable callback_args:
            Additional positional arguments to the callback callable.
        :param dictionary callback_kwargs:
            Keyword arguments to the callback callable.
        :param str help:
            Help text displayed in the usage information.
        :param str metavar:
            Name to use instead of the long option name for help text.

        The following parameters are for Flake8's option handling alone.

        :param bool parse_from_config:
            Whether or not this option should be parsed out of config files.
        :param bool comma_separated_list:
            Whether the option is a comma separated list when parsing from a
            config file.
        :param bool normalize_paths:
            Whether the option is expecting a path or list of paths and should
            attempt to normalize the paths to absolute paths.
        """
        self.short_option_name = short_option_name
        self.long_option_name = long_option_name
        self.option_args = filter(None, (short_option_name, long_option_name))
        self.option_kwargs = {
            'action': action,
            'default': default,
            'type': type,
            'dest': self._make_dest(dest),
            'callback': callback,
            'callback_args': callback_args,
            'callback_kwargs': callback_kwargs,
            'help': help,
            'metavar': metavar,
        }
        # Set attributes for our option arguments
        for key, value in self.option_kwargs.items():
            setattr(self, key, value)

        # Set our custom attributes
        self.parse_from_config = parse_from_config
        self.comma_separated_list = comma_separated_list
        self.normalize_paths = normalize_paths

        self.config_name = None
        if parse_from_config:
            if not long_option_name:
                raise ValueError('When specifying parse_from_config=True, '
                                 'a long_option_name must also be specified.')
            self.config_name = long_option_name[2:].replace('-', '_')

    def __repr__(self):
        """Simple representation of an Option class."""
        return (
            'Option({0}, {1}, action={action}, default={default}, '
            'dest={dest}, type={type}, callback={callback}, help={help},'
            ' callback={callback}, callback_args={callback_args}, '
            'callback_kwargs={callback_kwargs}, metavar={metavar})'
        ).format(self.short_option_name, self.long_option_name,
                 **self.option_kwargs)

    def _make_dest(self, dest):
        if dest:
            return dest

        if self.long_option_name:
            return self.long_option_name[2:].replace('-', '_')
        return self.short_option_name[1]

    def normalize(self, value):
        """Normalize the value based on the option configuration."""
        if self.normalize_paths:
            # Decide whether to parse a list of paths or a single path
            normalize = utils.normalize_path
            if self.comma_separated_list:
                normalize = utils.normalize_paths
            return normalize(value)
        elif self.comma_separated_list:
            return utils.parse_comma_separated_list(value)
        return value

    def to_optparse(self):
        """Convert a Flake8 Option to an optparse Option."""
        if not hasattr(self, '_opt'):
            self._opt = optparse.Option(*self.option_args,
                                        **self.option_kwargs)
        return self._opt


class OptionManager(object):
    """Manage Options and OptionParser while adding post-processing."""

    def __init__(self, prog=None, version=None,
                 usage='%prog [options] file file ...'):
        """Initialize an instance of an OptionManager.

        :param str prog:
            Name of the actual program (e.g., flake8).
        :param str version:
            Version string for the program.
        :param str usage:
            Basic usage string used by the OptionParser.
        """
        self.parser = optparse.OptionParser(prog=prog, version=version,
                                            usage=usage)
        self.config_options_dict = {}
        self.options = []
        self.program_name = prog
        self.version = version
        self.registered_plugins = set()

    @staticmethod
    def format_plugin(plugin_tuple):
        """Convert a plugin tuple into a dictionary mapping name to value."""
        return dict(zip(["entry", "name", "version"], plugin_tuple))

    def add_option(self, *args, **kwargs):
        """Create and register a new option.

        See parameters for :class:`~flake8.options.manager.Option` for
        acceptable arguments to this method.

        .. note::

            ``short_option_name`` and ``long_option_name`` may be specified
            positionally as they are with optparse normally.
        """
        if len(args) == 1 and args[0].startswith('--'):
            args = (None, args[0])
        option = Option(*args, **kwargs)
        self.parser.add_option(option.to_optparse())
        self.options.append(option)
        if option.parse_from_config:
            self.config_options_dict[option.config_name] = option
        LOG.debug('Registered option "%s".', option)

    def generate_versions(self, format_str='%(name)s: %(version)s'):
        """Generate a comma-separated list of versions of plugins."""
        return ', '.join(
            format_str % self.format_plugin(plugin)
            for plugin in self.registered_plugins
        )

    def update_version_string(self):
        """Update the flake8 version string."""
        self.parser.version = (self.version + ' (' +
                               self.generate_versions() + ')')

    def generate_epilog(self):
        """Create an epilog with the version and name of each of plugin."""
        plugin_version_format = '%(name)s(%(entry)s): %(version)s'
        self.parser.epilog = 'Installed plugins: ' + self.generate_versions(
            plugin_version_format
        )

    def parse_args(self, args=None, values=None):
        """Simple proxy to calling the OptionParser's parse_args method."""
        self.generate_epilog()
        self.update_version_string()
        options, xargs = self.parser.parse_args(args, values)
        for option in self.options:
            old_value = getattr(options, option.dest)
            setattr(options, option.dest, option.normalize(old_value))

        return options, xargs

    def register_plugin(self, entry_point_name, name, version):
        """Register a plugin relying on the OptionManager.

        :param str entry_point_name:
            The name of the entry-point loaded with pkg_resources. For
            example, if the entry-point looks like: ``C90 = mccabe.Checker``
            then the ``entry_point_name`` would be ``C90``.
        :param str name:
            The name of the checker itself. This will be the ``name``
            attribute of the class or function loaded from the entry-point.
        :param str version:
            The version of the checker that we're using.
        """
        self.registered_plugins.add((entry_point_name, name, version))
