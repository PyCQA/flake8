from __future__ import with_statement

import os
import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

from flake8 import engine
from flake8.util import is_windows


class IntegrationTestCase(unittest.TestCase):
    """Integration style tests to exercise different command line options."""

    def this_file(self):
        """Return the real path of this file."""
        this_file = os.path.realpath(__file__)
        if this_file.endswith("pyc"):
            this_file = this_file[:-1]
        return this_file

    def check_files(self, arglist=[], explicit_stdin=False, count=0):
        """Call check_files."""
        if explicit_stdin:
            target_file = "-"
        else:
            target_file = self.this_file()
        argv = ['flake8'] + arglist + [target_file]
        with mock.patch("sys.argv", argv):
            style_guide = engine.get_style_guide(parse_argv=True)
            report = style_guide.check_files()
        self.assertEqual(report.total_errors, count)
        return style_guide, report

    def test_no_args(self):
        # assert there are no reported errors
        self.check_files()

    def _job_tester(self, jobs):
        # mock stdout.flush so we can count the number of jobs created
        with mock.patch('sys.stdout.flush') as mocked:
            guide, report = self.check_files(arglist=['--jobs=%s' % jobs])
            if is_windows():
                # The code path where guide.options.jobs gets converted to an
                # int is not run on windows. So, do the int conversion here.
                self.assertEqual(int(guide.options.jobs), jobs)
                # On windows, call count is always zero.
                self.assertEqual(mocked.call_count, 0)
            else:
                self.assertEqual(guide.options.jobs, jobs)
                self.assertEqual(mocked.call_count, jobs)

    def test_jobs(self):
        self._job_tester(2)
        self._job_tester(10)

    def test_stdin(self):
        self.count = 0

        def fake_stdin():
            self.count += 1
            with open(self.this_file(), "r") as f:
                return f.read()

        with mock.patch("pep8.stdin_get_value", fake_stdin):
            guide, report = self.check_files(arglist=['--jobs=4'],
                                             explicit_stdin=True)
        self.assertEqual(self.count, 1)

    def test_stdin_fail(self):
        def fake_stdin():
            return "notathing\n"
        with mock.patch("pep8.stdin_get_value", fake_stdin):
            # only assert needed is in check_files
            guide, report = self.check_files(arglist=['--jobs=4'],
                                             explicit_stdin=True,
                                             count=1)
