"""Plugin built-in to Flake8 to treat pyflakes as a plugin."""
from __future__ import annotations

import argparse
import ast
import logging
from collections.abc import Generator
from typing import Any

import pyflakes.checker

from flake8.options.manager import OptionManager

LOG = logging.getLogger(__name__)

FLAKE8_PYFLAKES_CODES = {
    "UnusedImport": "F401",
    "ImportShadowedByLoopVar": "F402",
    "ImportStarUsed": "F403",
    "LateFutureImport": "F404",
    "ImportStarUsage": "F405",
    "ImportStarNotPermitted": "F406",
    "FutureFeatureNotDefined": "F407",
    "PercentFormatInvalidFormat": "F501",
    "PercentFormatExpectedMapping": "F502",
    "PercentFormatExpectedSequence": "F503",
    "PercentFormatExtraNamedArguments": "F504",
    "PercentFormatMissingArgument": "F505",
    "PercentFormatMixedPositionalAndNamed": "F506",
    "PercentFormatPositionalCountMismatch": "F507",
    "PercentFormatStarRequiresSequence": "F508",
    "PercentFormatUnsupportedFormatCharacter": "F509",
    "StringDotFormatInvalidFormat": "F521",
    "StringDotFormatExtraNamedArguments": "F522",
    "StringDotFormatExtraPositionalArguments": "F523",
    "StringDotFormatMissingArgument": "F524",
    "StringDotFormatMixingAutomatic": "F525",
    "FStringMissingPlaceholders": "F541",
    "TStringMissingPlaceholders": "F542",
    "MultiValueRepeatedKeyLiteral": "F601",
    "MultiValueRepeatedKeyVariable": "F602",
    "TooManyExpressionsInStarredAssignment": "F621",
    "TwoStarredExpressions": "F622",
    "AssertTuple": "F631",
    "IsLiteral": "F632",
    "InvalidPrintSyntax": "F633",
    "IfTuple": "F634",
    "BreakOutsideLoop": "F701",
    "ContinueOutsideLoop": "F702",
    "YieldOutsideFunction": "F704",
    "ReturnOutsideFunction": "F706",
    "DefaultExceptNotLast": "F707",
    "LazyImportNotAtModuleScope": "F708",
    "LazyImportStarNotPermitted": "F709",
    "DoctestSyntaxError": "F721",
    "ForwardAnnotationSyntaxError": "F722",
    "RedefinedWhileUnused": "F811",
    "UndefinedName": "F821",
    "UndefinedExport": "F822",
    "UndefinedLocal": "F823",
    "UnusedIndirectAssignment": "F824",
    "DuplicateArgument": "F831",
    "UnusedVariable": "F841",
    "UnusedAnnotation": "F842",
    "EagerUseOfLazyImport": "F851",
    "RaiseNotImplemented": "F901",
}


class FlakesChecker:
    """Subclass the Pyflakes checker to conform with the flake8 API."""

    _with_doctest = False
    _builtins = None

    def __init__(self, tree: ast.AST, filename: str) -> None:
        """Initialize the PyFlakes plugin with an AST tree and filename."""
        self._checker = pyflakes.checker.Checker(
            tree,
            filename=filename,
            builtins=self._builtins,
            withDoctest=self._with_doctest,
        )

    def run(self) -> Generator[tuple[int, int, str, type[Any]]]:
        """Run the plugin."""
        for message in self._checker.messages:
            col = getattr(message, "col", 0)
            yield (
                message.lineno,
                col,
                "{} {}".format(
                    FLAKE8_PYFLAKES_CODES.get(type(message).__name__, "F999"),
                    message.message % message.message_args,
                ),
                message.__class__,
            )

    @classmethod
    def add_options(cls, parser: OptionManager) -> None:
        """Register options for PyFlakes on the Flake8 OptionManager."""
        parser.add_option(
            "--builtins",
            parse_from_config=True,
            comma_separated_list=True,
            help="define more built-ins, comma separated",
        )
        parser.add_option(
            "--doctests",
            default=False,
            action="store_true",
            parse_from_config=True,
            help="also check syntax of the doctests",
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        """Parse option values from Flake8's OptionManager."""
        cls._builtins = options.builtins
        cls._with_doctest = options.doctests
