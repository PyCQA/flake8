"""Implementation of the StyleGuide used by Flake8."""


class StyleGuide(object):
    """Manage a Flake8 user's style guide."""

    def __init__(self, options, arguments, checker_plugins, listening_plugins,
                 formatting_plugins):
        """Initialize our StyleGuide.

        .. todo:: Add parameter documentation.
        """
        pass


# Should separate style guide logic from code that runs checks
# StyleGuide should manage select/ignore logic as well as include/exclude
# logic. See also https://github.com/PyCQA/pep8/pull/433

# StyleGuide shoud dispatch check execution in a way that can use
# multiprocessing but also retry in serial. See also:
# https://gitlab.com/pycqa/flake8/issues/74

# StyleGuide should interface with Reporter and aggregate errors/notify
# listeners
