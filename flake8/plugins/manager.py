"""Plugin loading and management logic and classes."""
import logging

import pkg_resources

LOG = logging.getLogger(__name__)


class Plugin(object):
    """Wrap an EntryPoint from setuptools and other logic."""

    def __init__(self, name, entry_point):
        """"Initialize our Plugin.

        :param str name:
            Name of the entry-point as it was registered with setuptools.
        :param entry_point:
            EntryPoint returned by setuptools.
        :type entry_point:
            setuptools.EntryPoint
        """
        self.name = name
        self.entry_point = entry_point
        self.plugin = None

    def __repr__(self):
        return 'Plugin(name="{0}", entry_point="{1}")'.format(
            self.name, self.entry_point
        )

    def execute(self, *args, **kwargs):
        r"""Call the plugin with \*args and \*\*kwargs."""
        return self.plugin(*args, **kwargs)

    def load(self, verify_requirements=False):
        """Retrieve the plugin for this entry-point.

        This loads the plugin, stores it on the instance and then returns it.
        It does not reload it after the first time, it merely returns the
        cached plugin.

        :param bool verify_requirements:
            Whether or not to make setuptools verify that the requirements for
            the plugin are satisfied.
        :returns:
            The plugin resolved from the entry-point.
        """
        if self.plugin is None:
            LOG.debug('Loading plugin "%s" from entry-point.', self.name)
            # Avoid relying on hasattr() here.
            resolve = getattr(self.entry_point, 'resolve', None)
            require = getattr(self.entry_point, 'require', None)
            if resolve and require:
                if verify_requirements:
                    LOG.debug('Verifying plugin "%s"\'s requirements.',
                              self.name)
                    require()
                self.plugin = resolve()
            else:
                self.plugin = self.entry_point.load(
                    require=verify_requirements
                )

        return self.plugin

    def provide_options(self, optmanager, options, extra_args):
        """Pass the parsed options and extra arguments to the plugin."""
        plugin = self.load()
        parse_options = getattr(plugin, 'parse_options', None)
        if parse_options is not None:
            LOG.debug('Providing options to plugin "%s".', self.name)
            try:
                parse_options(optmanager, options, extra_args)
            except TypeError:
                parse_options(options)

    def register_options(self, optmanager):
        """Register the plugin's command-line options on the OptionManager.

        :param optmanager:
            Instantiated OptionManager to register options on.
        :type optmanager:
            flake8.options.manager.OptionManager
        :returns:
            Nothing
        """
        plugin = self.load()
        add_options = getattr(plugin, 'add_options', None)
        if add_options is not None:
            LOG.debug(
                'Registering options from plugin "%s" on OptionManager %r',
                self.name, optmanager
            )
            plugin.add_options(optmanager)


class PluginManager(object):
    """Find and manage plugins consistently."""

    def __init__(self, namespace, verify_requirements=False):
        """Initialize the manager.

        :param str namespace:
            Namespace of the plugins to manage, e.g., 'flake8.extension'.
        :param bool verify_requirements:
            Whether or not to make setuptools verify that the requirements for
            the plugin are satisfied.
        """
        self.namespace = namespace
        self.verify_requirements = verify_requirements
        self.plugins = {}
        self.names = []
        self._load_all_plugins()

    def __contains__(self, name):
        LOG.debug('Checking for "%s" in plugin manager.', name)
        return name in self.plugins

    def __getitem__(self, name):
        LOG.debug('Retrieving plugin for "%s".', name)
        return self.plugins[name]

    def _load_all_plugins(self):
        LOG.debug('Loading entry-points for "%s".', self.namespace)
        for entry_point in pkg_resources.iter_entry_points(self.namespace):
            name = entry_point.name
            self.plugins[name] = Plugin(name, entry_point)
            self.names.append(name)
            LOG.info('Loaded %r for plugin "%s".', self.plugins[name], name)

    def map(self, func, *args, **kwargs):
        """Call ``func`` with the plugin and *args and **kwargs after.

        This yields the return value from ``func`` for each plugin.

        :param collections.Callable func:
            Function to call with each plugin. Signature should at least be:

            .. code-block:: python

                def myfunc(plugin):
                     pass

            Any extra positional or keyword arguments specified with map will
            be passed along to this function after the plugin.
        :param args:
            Positional arguments to pass to ``func`` after each plugin.
        :param kwargs:
            Keyword arguments to pass to ``func`` after each plugin.
        """
        for name in self.names:
            yield func(self.plugins[name], *args, **kwargs)


class Checkers(object):
    """All of the checkers registered through entry-ponits."""

    def __init__(self, namespace='flake8.extension'):
        """Initialize the Checkers collection."""
        self.manager = PluginManager(namespace)

    @property
    def names(self):
        return self.manager.names

    def register_options(self, optmanager):
        """Register all of the checkers' options to the OptionManager."""
        def call_register_options(plugin, optmanager):
            return plugin.register_options(optmanager)

        list(self.map(call_register_options, optmanager))

    def provide_options(self, optmanager, options, extra_args):
        def call_provide_options(plugin, optmanager, options, extra_args):
            return plugin.provide_options(optmanager, options, extra_args)

        list(self.map(call_provide_options, optmanager, options, extra_args))


class Listeners(object):
    """All of the listeners registered through entry-points."""

    def __init__(self, namespace='flake8.listener'):
        self.manager = PluginManager(namespace)

    @property
    def names(self):
        return self.manager.names


class ReportFormatters(object):
    """All of the report formatters registered through entry-points."""

    def __init__(self, namespace='flake8.report'):
        self.manager = PluginManager(namespace)

    @property
    def names(self):
        return self.manager.names
