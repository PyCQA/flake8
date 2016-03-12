"""Top-level module for Flake8.

This module

- initializes logging for the command-line tool
- tracks the version of the package
- provides a way to configure logging for the command-line tool

.. autofunction:: flake8.configure_logging

"""
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Shim for version of Python < 2.7."""

        def emit(self, record):
            """Do nothing."""
            pass
import sys

LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())

# Clean up after LOG config
del NullHandler

__version__ = '3.0.0a1'


_VERBOSITY_TO_LOG_LEVEL = {
    # output more than warnings but not debugging info
    1: logging.INFO,
    # output debugging information and everything else
    2: logging.DEBUG,
}

LOG_FORMAT = ('[%(name)-25s]:%(threadName)s %(relativeCreated)6d '
              '%(levelname)-8s %(message)s')


def configure_logging(verbosity, filename=None, logformat=LOG_FORMAT):
    """Configure logging for flake8.

    :param int verbosity:
        How verbose to be in logging information.
    :param str filename:
        Name of the file to append log information to.
        If ``None`` this will log to ``sys.stderr``.
        If the name is "stdout" or "stderr" this will log to the appropriate
        stream.
    """
    if verbosity <= 0:
        return
    if verbosity > 2:
        verbosity = 2

    log_level = _VERBOSITY_TO_LOG_LEVEL[verbosity]

    if not filename or filename in ('stderr', 'stdout'):
        fileobj = getattr(sys, filename or 'stderr')
        handler_cls = logging.StreamHandler
    else:
        fileobj = filename
        handler_cls = logging.FileHandler

    handler = handler_cls(fileobj)
    handler.setFormatter(logging.Formatter(logformat))
    LOG.addHandler(handler)
    LOG.setLevel(log_level)
    LOG.debug('Added a %s logging handler to logger root at %s',
              filename, __name__)
