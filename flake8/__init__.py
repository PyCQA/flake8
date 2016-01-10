import logging
import sys

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
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

    LOG.addHandler(handler)
    LOG.setLevel(log_level)
    LOG.debug('Added a %s logging handler to logger root at %s',
              filename, __name__)
