"""Contains the Violation error class used internally."""
from __future__ import annotations

import functools
import linecache
import logging
from typing import Match
from typing import NamedTuple

from flake8 import defaults
from flake8 import utils


LOG = logging.getLogger(__name__)


@functools.lru_cache(maxsize=512)
def _find_noqa(physical_line: str) -> Match[str] | None:
    return defaults.NOQA_INLINE_REGEXP.search(physical_line)


@functools.lru_cache(maxsize=512)
def _find_block_noqa(physical_line: str) -> Match[str] | None:
    return defaults.NOQA_BLOCK_REGEXP.search(physical_line)


@functools.lru_cache(maxsize=8)
def _noqa_block_ranges(filename: str) -> Match[str] | None:
    noqa_block_ranges = []
    next_expected_state = "on"
    current_block_start = None
    current_block_codes = None

    enumerated_lines = enumerate(linecache.getlines(filename), start=1)

    for line_no, physical_line in enumerated_lines:
        noqa_match = _find_block_noqa(physical_line)
        if noqa_match is None:
            continue

        state = noqa_match.groupdict().get("state").lower()
        codes = noqa_match.groupdict().get("codes")

        if state != next_expected_state:
            continue
        elif state == "on":
            next_expected_state = "off"
            current_block_start = line_no
            current_block_codes = codes
        elif state == "off":
            noqa_block_ranges.append((
                range(current_block_start, line_no), current_block_codes,
            ))
            next_expected_state = "on"
            current_block_start = None
            current_block_codes = None

    return tuple(noqa_block_ranges)


class Violation(NamedTuple):
    """Class representing a violation reported by Flake8."""

    code: str
    filename: str
    line_number: int
    column_number: int
    text: str
    physical_line: str | None

    def is_block_ignored(self, disable_noqa: bool) -> bool:
        """Determine if line is between comments which define an ignore block.

        :param disable_noqa:
            Whether or not users have provided ``--disable-noqa``.
        :returns:
            True if error is ignored by block, False otherwise.
        """
        if disable_noqa:
            return False

        filename = self.filename
        line_number = self.line_number

        def in_range(block_range):
            return line_number in block_range

        blocks_in_range = (
            (block_line_range, codes)
            for block_line_range, codes in _noqa_block_ranges(filename)
            for is_in_range, codes in [(in_range(block_line_range), codes)]
            if is_in_range
        )

        block_line_range, codes_str = next(blocks_in_range, (None, None))

        if block_line_range is None:
            LOG.debug("%r is not block ignored", self)
            return False

        if codes_str is None:
            LOG.debug("%r is ignored by a blanket ``# noqa: on ... # noqa: off`` block", self)
            return True

        codes = set(utils.parse_comma_separated_list(codes_str))
        if self.code in codes or self.code.startswith(tuple(codes)):
            LOG.debug(
                "%r is ignored specifically within ``# noqa: on %s ... # noqa: off`` block",
                self,
                codes_str,
            )
            return True

        LOG.debug(
            "%r is not ignored within ``# noqa: on %s ... # noqa: off`` block", self, codes_str
        )
        return False

    def is_inline_ignored(self, disable_noqa: bool) -> bool:
        """Determine if a comment has been added to ignore this line.

        :param disable_noqa:
            Whether or not users have provided ``--disable-noqa``.
        :returns:
            True if error is ignored in-line, False otherwise.
        """
        physical_line = self.physical_line
        # TODO(sigmavirus24): Determine how to handle stdin with linecache
        if disable_noqa:
            return False

        if physical_line is None:
            physical_line = linecache.getline(self.filename, self.line_number)
        noqa_match = _find_noqa(physical_line)
        if noqa_match is None:
            LOG.debug("%r is not inline ignored", self)
            return False

        codes_str = noqa_match.groupdict()["codes"]
        if codes_str is None:
            LOG.debug("%r is ignored by a blanket ``# noqa``", self)
            return True

        codes = set(utils.parse_comma_separated_list(codes_str))
        if self.code in codes or self.code.startswith(tuple(codes)):
            LOG.debug(
                "%r is ignored specifically inline with ``# noqa: %s``",
                self,
                codes_str,
            )
            return True

        LOG.debug(
            "%r is not ignored inline with ``# noqa: %s``", self, codes_str
        )
        return False
