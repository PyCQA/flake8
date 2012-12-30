from unittest import TestCase
from flakey import check, print_messages


code = """
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
        for c in (code, code2, code3):
            warnings = check(code, '(stdin)')
            warnings = print_messages(warnings)
            self.assertEqual(warnings, 0)

    def test_from_import_exception_in_scope(self):
        warnings = check(code_from_import_exception, '(stdin)')
        warnings = print_messages(warnings)
        self.assertEqual(warnings, 0)

    def test_import_exception_in_scope(self):
        warnings = check(code_import_exception, '(stdin)')
        warnings = print_messages(warnings)
        self.assertEqual(warnings, 0)
