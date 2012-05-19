from __future__ import with_statement
import re
import os


def skip_warning(warning):
    # XXX quick dirty hack, just need to keep the line in the warning
    if not os.path.isfile(warning.filename):
        return False

    # XXX should cache the file in memory
    with open(warning.filename) as f:
        line = f.readlines()[warning.lineno - 1]

    return skip_line(line)


def skip_line(line):
    return line.strip().lower().endswith('# noqa')


_NOQA = re.compile(r'flake8[:=]\s*noqa', re.I | re.M)


def skip_file(path):
    """Returns True if this header is found in path

    # flake8: noqa
    """
    f = open(path)
    try:
        content = f.read()
    finally:
        f.close()
    return _NOQA.search(content) is not None
