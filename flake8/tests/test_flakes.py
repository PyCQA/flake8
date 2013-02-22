# -*- coding: utf-8 -*-
import sys

from unittest import TestCase
from pyflakes.api import check


class FlakesTestReporter(object):
    def __init__(self):
        self.messages = []
        self.flakes = self.messages.append

    def unexpectedError(self, filename, msg):
        self.flakes('[unexpectedError] %s: %s' % (filename, msg))

    def syntaxError(self, filename, msg, lineno, offset, text):
        self.flakes('[syntaxError] %s:%d: %s' % (filename, lineno, msg))


code0 = """
try:
    pass
except ValueError, err:
    print(err)
"""

code1 = """
try:
    pass
except ValueError as err:
    print(err)
"""

code2 = """
try:
    pass
except ValueError:
    print("err")

try:
    pass
except ValueError:
    print("err")
"""

code3 = """
try:
    pass
except (ImportError, ValueError):
    print("err")
"""

code_from_import_exception = """
from foo import SomeException
try:
    pass
except SomeException:
    print("err")
"""

code_import_exception = """
import foo.SomeException
try:
    pass
except foo.SomeException:
    print("err")
"""


class TestFlake(TestCase):

    def test_exception(self):
        codes = [code1, code2, code3]
        if sys.version_info < (2, 6):
            codes[0] = code0
        elif sys.version_info < (3,):
            codes.insert(0, code0)
        for code in codes:
            reporter = FlakesTestReporter()
            warnings = check(code, '(stdin)', reporter)
            self.assertFalse(reporter.messages)
            self.assertEqual(warnings, 0)

    def test_from_import_exception_in_scope(self):
        reporter = FlakesTestReporter()
        warnings = check(code_from_import_exception, '(stdin)', reporter)
        self.assertFalse(reporter.messages)
        self.assertEqual(warnings, 0)

    def test_import_exception_in_scope(self):
        reporter = FlakesTestReporter()
        warnings = check(code_import_exception, '(stdin)', reporter)
        self.assertFalse(reporter.messages)
        self.assertEqual(warnings, 0)
