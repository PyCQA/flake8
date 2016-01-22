"""Exception classes for all of Flake8."""


class Flake8Exception(Exception):
    """Plain Flake8 exception."""

    pass


class FailedToLoadPlugin(Flake8Exception):
    """Exception raised when a plugin fails to load."""

    FORMAT = 'Flake8 failed to load plugin "%(name)s" due to %(exc)s.'

    def __init__(self, *args, **kwargs):
        """Initialize our FailedToLoadPlugin exception."""
        self.plugin = kwargs.pop('plugin')
        self.ep_name = self.plugin.name
        self.original_exception = kwargs.pop('exception')
        super(FailedToLoadPlugin, self).__init__(*args, **kwargs)

    def __str__(self):
        """Return a nice string for our exception."""
        return self.FORMAT % {'name': self.ep_name,
                              'exc': self.original_exception}
