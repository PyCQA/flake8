import unittest
import sys
from StringIO import StringIO

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
        wanted = ["stdin:5:1: 'a' is too complex (3)",
                  'stdin:Loop 2 is too complex (1)']
        self.assertEqual(res, wanted)
