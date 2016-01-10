"""Utility methods for flake8."""
import os


def parse_comma_separated_list(value):
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
    """Parse a comma-separated list of paths.

    :returns:
        The normalized paths.
    :rtype:
        [str]
    """
    return [normalize_path(p) for p in parse_comma_separated_list(paths)]


def normalize_path(path, parent=os.curdir):
    """Normalize a single-path.

    :returns:
        The normalized path.
    :rtype:
        str
    """
    if '/' in path:
        path = os.path.abspath(os.path.join(parent, path))
    return path.rstrip('/')
