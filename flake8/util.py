import re


def skip_warning(warning):
    # XXX quick dirty hack, just need to keep the line in the warning
    line = open(warning.filename).readlines()[warning.lineno - 1]
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
