from unittest import TestCase
from flake8.pyflakes import check


code = """
try:
    pass
except ValueError as err:
    print(err)
"""


class TestFlake(TestCase):

    def test_exception(self):
        warnings = check(code)
        self.assertEqual(warnings, 0)
