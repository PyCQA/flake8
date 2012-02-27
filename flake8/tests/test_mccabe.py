import unittest
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO     # NOQA

from flake8.mccabe import get_code_complexity


_GLOBAL = """\

for i in range(10):
    pass

def a():
    def b():
        def c():
            pass
        c()
    b()

"""


class McCabeTest(unittest.TestCase):

    def setUp(self):
        self.old = sys.stdout
        self.out = sys.stdout = StringIO()

    def tearDown(self):
        sys.sdtout = self.old

    def test_sample(self):
        self.assertEqual(get_code_complexity(_GLOBAL, 1), 2)
        self.out.seek(0)
        res = self.out.read().strip().split('\n')
        wanted = ["stdin:5:1: W901 'a' is too complex (4)",
                  "stdin:2:1: W901 'Loop 2' is too complex (2)"]
        self.assertEqual(res, wanted)
