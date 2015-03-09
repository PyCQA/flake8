from __future__ import with_statement

import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

import setuptools
from flake8 import main


class TestMain(unittest.TestCase):
    def setUp(self):
        self.patches = {}

    def tearDown(self):
        assert len(self.patches.items()) == 0

    def start_patch(self, patch):
        self.patches[patch] = mock.patch(patch)
        return self.patches[patch].start()

    def stop_patches(self):
        patches = self.patches.copy()
        for k, v in patches.items():
            v.stop()
            del(self.patches[k])

    def test_issue_39_regression(self):
        distribution = setuptools.Distribution()
        cmd = main.Flake8Command(distribution)
        cmd.options_dict = {}
        cmd.run()


if __name__ == '__main__':
    unittest.main()
