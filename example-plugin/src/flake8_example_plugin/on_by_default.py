"""Our first example plugin."""
from __future__ import annotations


class ExampleOne:
    """First Example Plugin."""

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        """Do nothing."""
        yield from []
