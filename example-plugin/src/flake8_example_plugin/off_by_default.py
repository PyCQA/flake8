"""Our first example plugin."""
from __future__ import annotations


class ExampleTwo:
    """Second Example Plugin."""

    off_by_default = True

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        """Do nothing."""
        yield (
            1,
            0,
            "X200 The off-by-default plugin was enabled",
            "OffByDefaultPlugin",
        )
