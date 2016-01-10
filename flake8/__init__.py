"""Top-level module for Flake8.

This module

- initializes logging for the command-line tool
- tracks the version of the package
- provides a way to configure logging for the command-line tool

.. autofunction:: flake8.configure_logging

"""
import logging
import sys

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Shim for version of Python < 2.7."""

        def emit(self, record):
            """Do nothing."""
            pass

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


def configure_logging(verbosity, filename=None):
    """Configure logging for flake8.

    :param int verbosity:
        How verbose to be in logging information.
    :param str filename:
        Name of the file to append log information to.
        If ``None`` this will log to ``sys.stderr``.
        If the name is "stdout" or "stderr" this will log to the appropriate
        stream.
    """
    global LOG
    if verbosity <= 0:
        return
    if verbosity > 2:
        verbosity = 2

    log_level = _VERBOSITY_TO_LOG_LEVEL[verbosity]

    if not filename or filename in ('stderr', 'stdout'):
        handler = logging.StreamHandler(getattr(sys, filename))
    else:
        handler = logging.FileHandler(filename)

    handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    )
    LOG.addHandler(handler)
    LOG.setLevel(log_level)
    LOG.debug('Added a %s logging handler to logger root at %s',
              filename, __name__)
