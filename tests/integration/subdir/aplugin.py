"""Module that is off sys.path by default, for testing local-plugin-paths."""


class ExtensionTestPlugin2:
    """Extension test plugin in its own directory."""

    def __init__(self, tree):
        """Construct an instance of test plugin."""

    def run(self):
        """Do nothing."""
