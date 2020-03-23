"""Module that is off sys.path by default, for testing local-plugin-paths."""


class ExtensionTestPlugin2(object):
    """Extension test plugin in its own directory."""

    name = 'ExtensionTestPlugin2'
    version = '1.0.0'

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""
