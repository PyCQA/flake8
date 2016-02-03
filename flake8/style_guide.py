"""Implementation of the StyleGuide used by Flake8."""
import enum

__all__ = (
    'StyleGuide',
)


class Selected(enum.Enum):
    """Enum representing an explicitly or implicitly selected code."""

    Explicitly = 'explicitly selected'
    Implicitly = 'implicitly selected'


class Ignored(enum.Enum):
    """Enum representing an explicitly or implicitly ignored code."""

    Explicitly = 'explicitly ignored'
    Implicitly = 'implicitly ignored'


class Decision(enum.Enum):
    """Enum representing whether a code should be ignored or selected."""

    Ignored = 'ignored error'
    Selected = 'selected error'


class StyleGuide(object):
    """Manage a Flake8 user's style guide."""

    def __init__(self, options, arguments, checker_plugins, listening_plugins,
                 formatting_plugins):
        """Initialize our StyleGuide.

        .. todo:: Add parameter documentation.
        """
        self.options = options
        self.arguments = arguments
        self.checkers = checker_plugins
        self.listeners = listening_plugins
        self.formatters = formatting_plugins
        self._selected = tuple(options.select)
        self._ignored = tuple(options.ignore)
        self._decision_cache = {}

    def is_user_selected(self, code):
        """Determine if the code has been selected by the user.

        :param str code:
            The code for the check that has been run.
        :returns:
            Selected.Implicitly if the selected list is empty,
            Selected.Explicitly if the selected list is not empty and a match
            was found,
            Ignored.Implicitly if the selected list is not empty but no match
            was found.
        """
        if not self._selected:
            return Selected.Implicitly

        if code.startswith(self._selected):
            return Selected.Explicitly

        return Ignored.Implicitly

    def is_user_ignored(self, code):
        """Determine if the code has been ignored by the user.

        :param str code:
            The code for the check that has been run.
        :returns:
            Selected.Implicitly if the ignored list is empty,
            Ignored.Explicitly if the ignored list is not empty and a match was
            found,
            Selected.Implicitly if the ignored list is not empty but no match
            was found.
        """
        if self._ignored and code.startswith(self._ignored):
            return Ignored.Explicitly

        return Selected.Implicitly

    def _decision_for(self, code):
        startswith = code.startswith
        selected = sorted([s for s in self._selected if startswith(s)])[0]
        ignored = sorted([i for i in self._ignored if startswith(i)])[0]

        if selected.startswith(ignored):
            return Decision.Selected
        return Decision.Ignored

    def should_report_error(self, code):
        """Determine if the error code should be reported or ignored.

        :param str code:
            The code for the check that has been run.
        """
        decision = self._decision_cache.get(code)
        if decision is None:
            selected = self.is_user_selected(code)
            ignored = self.is_user_ignored(code)

            if ((selected is Selected.Explicitly or
                    selected is Selected.Implicitly) and
                    ignored is Selected.Implicitly):
                decision = Decision.Selected
            elif (selected is Selected.Explicitly and
                    ignored is Ignored.Explicitly):
                decision = self._decision_for(code)
            elif (selected is Ignored.Implicitly or
                    ignored is Ignored.Explicitly):
                decision = Decision.Ignored

            self._decision_cache[code] = decision
        return decision


# Should separate style guide logic from code that runs checks
# StyleGuide should manage select/ignore logic as well as include/exclude
# logic. See also https://github.com/PyCQA/pep8/pull/433

# StyleGuide shoud dispatch check execution in a way that can use
# multiprocessing but also retry in serial. See also:
# https://gitlab.com/pycqa/flake8/issues/74

# StyleGuide should interface with Reporter and aggregate errors/notify
# listeners
