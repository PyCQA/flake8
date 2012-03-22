from unittest import TestCase
from flake8.pyflakes import check


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
            warnings = check(code)
            self.assertEqual(warnings, 0, code)

    def test_from_import_exception_in_scope(self):
        self.assertEqual(check(code_from_import_exception), 0)

    def test_import_exception_in_scope(self):
        self.assertEqual(check(code_import_exception), 0)
