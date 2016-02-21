"""Utility methods for flake8."""
import io
import os
import sys


def parse_comma_separated_list(value):
    # type: (Union[Sequence[str], str]) -> List[str]
    """Parse a comma-separated list.

    :param value:
        String or list of strings to be parsed and normalized.
    :returns:
        List of values with whitespace stripped.
    :rtype:
        list
    """
    if not value:
        return []

    if not isinstance(value, (list, tuple)):
        value = value.split(',')

    return [item.strip() for item in value]


def normalize_paths(paths, parent=os.curdir):
    # type: (Union[Sequence[str], str], str) -> List[str]
    """Parse a comma-separated list of paths.

    :returns:
        The normalized paths.
    :rtype:
        [str]
    """
    return [normalize_path(p, parent)
            for p in parse_comma_separated_list(paths)]


def normalize_path(path, parent=os.curdir):
    # type: (str, str) -> str
    """Normalize a single-path.

    :returns:
        The normalized path.
    :rtype:
        str
    """
    if '/' in path:
        path = os.path.abspath(os.path.join(parent, path))
    return path.rstrip('/')


def stdin_get_value():
    # type: () -> str
    """Get and cache it so plugins can use it."""
    cached_value = getattr(stdin_get_value, 'cached_stdin', None)
    if cached_value is None:
        stdin_value = sys.stdin.read()
        if sys.version_info < (3, 0):
            cached_type = io.BytesIO
        else:
            cached_type = io.StringIO
        stdin_get_value.cached_stdin = cached_type(stdin_value)
    return cached_value.getvalue()


def is_windows():
    # type: () -> bool
    """Determine if we're running on Windows.

    :returns:
        True if running on Windows, otherwise False
    :rtype:
        bool
    """
    return os.name == 'nt'


def is_using_stdin(paths):
    # type: (List[str]) -> bool
    """Determine if we're going to read from stdin.

    :param list paths:
        The paths that we're going to check.
    :returns:
        True if stdin (-) is in the path, otherwise False
    :rtype:
        bool
    """
    return '-' in paths
