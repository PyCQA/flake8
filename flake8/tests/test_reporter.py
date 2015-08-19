from __future__ import with_statement

import errno
import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

from flake8 import reporter


def ioerror_report_factory(errno_code):
    class IOErrorBaseQReport(reporter.BaseQReport):
        def _process_main(self):
            raise IOError(errno_code, 'Fake bad pipe exception')

    options = mock.MagicMock()
    options.jobs = 2
    return IOErrorBaseQReport(options)


class TestBaseQReport(unittest.TestCase):
    def test_does_not_raise_a_bad_pipe_ioerror(self):
        """Test that no EPIPE IOError exception is re-raised or leaked."""
        report = ioerror_report_factory(errno.EPIPE)
        try:
            report.process_main()
        except IOError:
            self.fail('BaseQReport.process_main raised an IOError for EPIPE'
                      ' but it should have caught this exception.')

    def test_raises_a_enoent_ioerror(self):
        """Test that an ENOENT IOError exception is re-raised."""
        report = ioerror_report_factory(errno.ENOENT)
        self.assertRaises(IOError, report.process_main)
