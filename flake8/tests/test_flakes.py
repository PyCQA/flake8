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
    print(err)

try:
    pass
except ValueError:
    print(err)
"""


class TestFlake(TestCase):

    def test_exception(self):
        for c in (code, code2):
            warnings = check(code)
            self.assertEqual(warnings, 0)
