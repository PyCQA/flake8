"""Implementation of the StyleGuide used by Flake8."""
import collections
import linecache
import logging
import re

import enum

from flake8 import utils

__all__ = (
    'StyleGuide',
)

LOG = logging.getLogger(__name__)


# TODO(sigmavirus24): Determine if we need to use enum/enum34
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


Error = collections.namedtuple('Error', ['code',
                                         'filename',
                                         'line_number',
                                         'column_number',
                                         'text'])


class StyleGuide(object):
    """Manage a Flake8 user's style guide."""

    NOQA_INLINE_REGEXP = re.compile(
        # We're looking for items that look like this:
        # ``# noqa``
        # ``# noqa: E123``
        # ``# noqa: E123,W451,F921``
        # ``# NoQA: E123,W451,F921``
        # ``# NOQA: E123,W451,F921``
        # We do not care about the ``: `` that follows ``noqa``
        # We do not care about the casing of ``noqa``
        # We want a comma-separated list of errors
        '# noqa(?:: )?(?P<codes>[A-Z0-9,]+)?$',
        re.IGNORECASE
    )

    def __init__(self, options, arguments, listener_trie, formatter):
        """Initialize our StyleGuide.

        .. todo:: Add parameter documentation.
        """
        self.options = options
        self.arguments = arguments
        self.listener = listener_trie
        self.formatter = formatter
        self._selected = tuple(options.select)
        self._ignored = tuple(options.ignore)
        self._decision_cache = {}

    def is_user_selected(self, code):
        # type: (Error) -> Union[Selected, Ignored]
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
        # type: (Error) -> Union[Selected, Ignored]
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
        # type: (Error) -> Decision
        startswith = code.startswith
        selected = sorted([s for s in self._selected if startswith(s)])[0]
        ignored = sorted([i for i in self._ignored if startswith(i)])[0]

        if selected.startswith(ignored):
            return Decision.Selected
        return Decision.Ignored

    def should_report_error(self, code):
        # type: (Error) -> Decision
        """Determine if the error code should be reported or ignored.

        This method only cares about the select and ignore rules as specified
        by the user in their configuration files and command-line flags.

        This method does not look at whether the specific line is being
        ignored in the file itself.

        :param str code:
            The code for the check that has been run.
        """
        decision = self._decision_cache.get(code)
        if decision is None:
            LOG.debug('Deciding if "%s" should be reported', code)
            selected = self.is_user_selected(code)
            ignored = self.is_user_ignored(code)
            LOG.debug('The user configured "%s" to be "%s", "%s"',
                      code, selected, ignored)

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
            LOG.debug('"%s" will be "%s"', code, decision)
        return decision

    def is_inline_ignored(self, error):
        """Determine if an comment has been added to ignore this line."""
        physical_line = linecache.getline(error.filename, error.line_number)
        noqa_match = self.NOQA_INLINE_REGEXP.search(physical_line)
        if noqa_match is None:
            LOG.debug('%r is not inline ignored', error)
            return False

        codes_str = noqa_match.groupdict()['codes']
        if codes_str is None:
            LOG.debug('%r is ignored by a blanket ``# noqa``', error)
            return True

        codes = set(utils.parse_comma_separated_list(codes_str))
        if error.code in codes or error.code.startswith(tuple(codes)):
            LOG.debug('%r is ignored specifically inline with ``# noqa: %s``',
                      error, codes_str)
            return True

        LOG.debug('%r is not ignored inline with ``# noqa: %s``',
                  error, codes_str)
        return False

    def handle_error(self, code, filename, line_number, column_number, text):
        # type: (str, str, int, int, str) -> NoneType
        """Handle an error reported by a check."""
        error = Error(code, filename, line_number, column_number, text)
        if (self.should_report_error(error.code) is Decision.Selected and
                self.is_inline_ignored(error) is False):
            self.formatter.handle(error)
            self.listener.notify(error.code, error)

# Should separate style guide logic from code that runs checks
# StyleGuide should manage select/ignore logic as well as include/exclude
# logic. See also https://github.com/PyCQA/pep8/pull/433

# StyleGuide shoud dispatch check execution in a way that can use
# multiprocessing but also retry in serial. See also:
# https://gitlab.com/pycqa/flake8/issues/74

# StyleGuide should interface with Reporter and aggregate errors/notify
# listeners
