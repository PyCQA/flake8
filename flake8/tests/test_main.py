from __future__ import with_statement

import unittest

import setuptools
from flake8 import main


class TestMain(unittest.TestCase):
    def test_issue_39_regression(self):
        distribution = setuptools.Distribution()
        cmd = main.Flake8Command(distribution)
        cmd.options_dict = {}
        cmd.run()


if __name__ == '__main__':
    unittest.main()
