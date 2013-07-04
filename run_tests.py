#!/usr/bin/env python

import unittest
import os
import re
import sys
sys.path.insert(0, '.')

TEST_DIR = 'flake8.tests'


def collect_tests():
    # list files in directory tests/
    names = os.listdir(TEST_DIR.replace('.', '/'))
    regex = re.compile("(?!_+)\w+\.py$")
    join = '.'.join
    # Make a list of the names like 'tests.test_name'
    names = [join([TEST_DIR, f[:-3]]) for f in names if regex.match(f)]
    modules = [__import__(name, fromlist=[TEST_DIR]) for name in names]
    load_tests = unittest.defaultTestLoader.loadTestsFromModule
    suites = [load_tests(m) for m in modules]
    suite = suites.pop()
    for s in suites:
        suite.addTests(s)
    return suite

if __name__ == "__main__":
    suite = collect_tests()
    res = unittest.TextTestRunner(verbosity=1).run(suite)

    # If it was successful, we don't want to exit with code 1
    raise SystemExit(not res.wasSuccessful())
