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

# The Problem
# ------------
#
# Some of the tests in this module pass when this module is run on its own, but
# they fail when this module is run as part of the whole test suite. These are
# the problematic tests:
#
#   test_jobs_verbose
#   test_stdin_jobs_warning
#
# On some platforms, the warnings.capture_warnings function doesn't work
# properly when run with the other flake8 tests. It drops some warnings, even
# though the warnings filter is set to 'always'. However, when run separately,
# these tests pass.
#
# This problem only occurs on Windows, with Python 3.3 and older. Maybe it's
# related to PEP 446 - Inheritable file descriptors?
#
#
#
#
# Things that didn't work
# ------------
#
# Nose --attr
#   I tried using the nosetests --attr feature to run the tests separately. I
#   put the following in setup.cfg
#
#   [nosetests]
#   atttr=!run_alone
#
#   Then I added a tox section thst did this
#
#   nosetests --attr=run_alone
#
#   However, the command line --attr would not override the config file --attr,
#   so the special tox section wound up runing all the tests, and failing.
#
#
#
# Nose --with-isolation
#   The nosetests --with-isolation flag did not help.
#
#
#
# unittest.skipIf
#   I tried decorating the problematic tests with the unittest.skipIf
#   decorator.
#
#    @unittest.skipIf(is_windows() and sys.version_info < (3, 4),
#                     "Fails on Windows with Python < 3.4 when run with other"
#                     " tests.")
#
#   The idea is, skip the tests in the main test run, on affected platforms.
#   Then, only on those platforms, come back in later and run the tests
#   separately.
#
#   I added a new stanza to tox.ini, to run the tests separately on the
#   affected platforms.
#
#   nosetests --no-skip
#
#   I ran in to a bug in the nosetests skip plugin. It would report the test as
#   having been run, but it would not actually run the test. So, when run with
#   --no-skip, the following test would be reported as having run and passed!
#
#   @unittest.skip("This passes o_o")
#   def test_should_fail(self):
#       assert 0
#
#   This bug has been reported here:
#   "--no-skip broken with Python 2.7"
#   https://github.com/nose-devs/nose/issues/512
#
#
#
# py.test
#
#   I tried using py.test, and its @pytest.mark.xfail decorator. I added some
#   separate stanzas in tox, and useing the pytest --runxfail option to run the
#   tests separately. This allows us to run all the tests together, on
#   platforms that allow it. On platforms that don't allow us to run the tests
#   all together, this still runs all the tests, but in two separate steps.
#
#   This is the same solution as the nosetests --no-skip solution I described
#   above, but --runxfail does not have the same bug as --no-skip.
#
#   This has the advantage that all tests are discoverable by default, outside
#   of tox. However, nose does not recognize the pytest.mark.xfail decorator.
#   So, if a user runs nosetests, it still tries to run the problematic tests
#   together with the rest of the test suite, causing them to fail.
#
#
#
#
#
#
# Solution
# ------------
# Move the problematic tests to _test_warnings.py, so nose.collector will not
# find them. Set up a separate section in tox.ini that runs this:
#
#     nosetests flake8.tests._test_warnings
#
# This allows all tests to pass on all platforms, when run through tox.
# However, it means that, even on unaffected platforms, the problematic tests
# are not discovered and run outside of tox (if the user just runs nosetests
# manually, for example).


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
        # the warnings.
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

        with mock.patch("pycodestyle.stdin_get_value", fake_stdin):
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
