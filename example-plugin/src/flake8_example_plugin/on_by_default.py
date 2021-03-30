"""Our first example plugin."""


class ExampleOne:
    """First Example Plugin."""
    name = 'on-by-default-example-plugin'
    version = '1.0.0'

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        """Do nothing."""
        yield from []
