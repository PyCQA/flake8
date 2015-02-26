"""
    _test_warnings.py

    Tests for the warnings that are emitted by flake8.

    This module is named _test_warnings instead of test_warnings so that a
    normal nosetests run does not collect it. The tests in this module pass
    when they are run alone, but they fail when they are run along with other
    tests (nosetests --with-isolation doesn't help).

    In tox.ini, these tests are run separately.
"""

from __future__ import with_statement

import os
import warnings
import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

from flake8 import engine
from flake8.util import is_windows


class IntegrationTestCaseWarnings(unittest.TestCase):
    """Integration style tests to check that warnings are issued properly for
    different command line options."""

    windows_warning_text = ("The --jobs option is not available on Windows."
                            " Ignoring --jobs arguments.")
    stdin_warning_text = ("The --jobs option is not compatible with"
                          " supplying input using - . Ignoring --jobs"
                          " arguments.")

    def this_file(self):
        """Return the real path of this file."""
        this_file = os.path.realpath(__file__)
        if this_file.endswith("pyc"):
            this_file = this_file[:-1]
        return this_file

    @staticmethod
    def get_style_guide_with_warnings(engine, *args, **kwargs):
        """
        Return a style guide object (obtained by calling
        engine.get_style_guide) and a list of the warnings that were raised in
        the process.

        Note: not threadsafe
        """

        # Note
        # https://docs.python.org/2/library/warnings.html
        #
        # The catch_warnings manager works by replacing and then later
        # restoring the module's showwarning() function and internal list of
        # filter specifications. This means the context manager is modifying
        # global state and therefore is not thread-safe

        with warnings.catch_warnings(record=True) as collected_warnings:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")

            # Get the style guide
            style_guide = engine.get_style_guide(*args, **kwargs)

        # Now that the warnings have been collected, return the style guide and
        # the
        # warnings.
        return (style_guide, collected_warnings)

    def verify_warnings(self, collected_warnings, expected_warnings):
        """
        Verifies that collected_warnings is a sequence that contains user
        warnings that match the sequence of string values passed in as
        expected_warnings.
        """
        if expected_warnings is None:
            expected_warnings = []

        collected_user_warnings = [w for w in collected_warnings
                                   if issubclass(w.category, UserWarning)]

        self.assertEqual(len(collected_user_warnings),
                         len(expected_warnings))

        collected_warnings_set = set(str(warning.message)
                                     for warning
                                     in collected_user_warnings)
        expected_warnings_set = set(expected_warnings)
        self.assertEqual(collected_warnings_set, expected_warnings_set)

    def check_files_collect_warnings(self,
                                     arglist=[],
                                     explicit_stdin=False,
                                     count=0,
                                     verbose=False):
        """Call check_files and collect any warnings that are issued."""
        if verbose:
            arglist.append('--verbose')
        if explicit_stdin:
            target_file = "-"
        else:
            target_file = self.this_file()
        argv = ['flake8'] + arglist + [target_file]
        with mock.patch("sys.argv", argv):
            (style_guide,
             collected_warnings,
             ) = self.get_style_guide_with_warnings(engine,
                                                    parse_argv=True)
            report = style_guide.check_files()
        self.assertEqual(report.total_errors, count)
        return style_guide, report, collected_warnings

    def check_files_no_warnings_allowed(self,
                                        arglist=[],
                                        explicit_stdin=False,
                                        count=0,
                                        verbose=False):
        """Call check_files, and assert that there were no warnings issued."""
        (style_guide,
         report,
         collected_warnings,
         ) = self.check_files_collect_warnings(arglist=arglist,
                                               explicit_stdin=explicit_stdin,
                                               count=count,
                                               verbose=verbose)
        self.verify_warnings(collected_warnings, expected_warnings=None)
        return style_guide, report

    def _job_tester(self, jobs, verbose=False):
        # mock stdout.flush so we can count the number of jobs created
        with mock.patch('sys.stdout.flush') as mocked:
            (guide,
             report,
             collected_warnings,
             ) = self.check_files_collect_warnings(
                arglist=['--jobs=%s' % jobs],
                verbose=verbose)

            if is_windows():
                # The code path where guide.options.jobs gets converted to an
                # int is not run on windows. So, do the int conversion here.
                self.assertEqual(int(guide.options.jobs), jobs)
                # On windows, call count is always zero.
                self.assertEqual(mocked.call_count, 0)
            else:
                self.assertEqual(guide.options.jobs, jobs)
                self.assertEqual(mocked.call_count, jobs)

            expected_warings = []
            if verbose and is_windows():
                expected_warings.append(self.windows_warning_text)
            self.verify_warnings(collected_warnings, expected_warings)

    def test_jobs(self, verbose=False):
        self._job_tester(2, verbose=verbose)
        self._job_tester(10, verbose=verbose)

    def test_no_args_no_warnings(self, verbose=False):
        self.check_files_no_warnings_allowed(verbose=verbose)

    def test_stdin_jobs_warning(self, verbose=False):
        self.count = 0

        def fake_stdin():
            self.count += 1
            with open(self.this_file(), "r") as f:
                return f.read()

        with mock.patch("pep8.stdin_get_value", fake_stdin):
            (style_guide,
             report,
             collected_warnings,
             ) = self.check_files_collect_warnings(arglist=['--jobs=4'],
                                                   explicit_stdin=True,
                                                   verbose=verbose)
            expected_warings = []
            if verbose:
                expected_warings.append(self.stdin_warning_text)
                if is_windows():
                    expected_warings.append(self.windows_warning_text)
            self.verify_warnings(collected_warnings, expected_warings)
        self.assertEqual(self.count, 1)

    def test_jobs_verbose(self):
        self.test_jobs(verbose=True)

    def test_no_args_no_warnings_verbose(self):
        self.test_no_args_no_warnings(verbose=True)

    def test_stdin_jobs_warning_verbose(self):
        self.test_stdin_jobs_warning(verbose=True)


if __name__ == '__main__':
    unittest.main()
