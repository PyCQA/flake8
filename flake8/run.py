
"""
Implementation of the command-line I{flake8} tool.
"""
import sys
import os
import os.path

from flake8.util import skip_file
from flake8 import pep8
from flake8 import pyflakes
from flake8 import mccabe


def check_file(path, complexity=-1):
    warnings = pyflakes.checkPath(path)
    warnings += pep8.input_file(path)
    if complexity > -1:
        warnings += mccabe.get_module_complexity(path, complexity)
    return warnings


def check_code(code, complexity=-1):
    warnings = pyflakes.check(code, '<stdin>')
    if complexity > -1:
        warnings += mccabe.get_code_complexity(code, complexity)
    return warnings


def _get_python_files(paths):
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if not filename.endswith('.py'):
                        continue
                    fullpath = os.path.join(dirpath, filename)
                    if not skip_file(fullpath):
                        yield fullpath

        else:
            if not skip_file(path):
                yield path


def main():
    options, args = pep8.process_options()
    complexity = options.max_complexity
    warnings = 0
    if args:
        for path in _get_python_files(args):
            warnings += check_file(path, complexity)
    else:
        stdin = sys.stdin.read()
        warnings += check_code(stdin, complexity)

    raise SystemExit(warnings > 0)


def _get_files(repo, **kwargs):
    seen = set()
    for rev in xrange(repo[kwargs['node']], len(repo)):
        for file_ in repo[rev].files():
            file_ = os.path.join(repo.root, file_)
            if file_ in seen or not os.path.exists(file_):
                continue
            seen.add(file_)
            if not file_.endswith('.py'):
                continue
            if skip_file(file_):
                continue
            yield file_


class _PEP8Options(object):
    # Default options taken from pep8.process_options()
    max_complexity = -1
    verbose = False
    quiet = False
    no_repeat = False
    exclude = [exc.rstrip('/') for exc in pep8.DEFAULT_EXCLUDE.split(',')]
    filename = ['*.py']
    select = []
    ignore = pep8.DEFAULT_IGNORE.split(',')  # or []?
    show_source = False
    show_pep8 = False
    statistics = False
    count = False
    benchmark = False
    testsuite = ''
    doctest = False


def hg_hook(ui, repo, **kwargs):
    # default pep8 setup
    pep8.options = _PEP8Options()
    pep8.options.physical_checks = pep8.find_checks('physical_line')
    pep8.options.logical_checks = pep8.find_checks('logical_line')
    pep8.options.counters = dict.fromkeys(pep8.BENCHMARK_KEYS, 0)
    pep8.options.messages = {}
    pep8.args = []
    complexity = ui.configint('flake8', 'complexity', default=-1)
    warnings = 0

    for file_ in _get_files(repo, **kwargs):
        warnings += check_file(file_, complexity)

    strict = ui.configbool('flake8', 'strict', default=True)

    if strict:
        return warnings

    return 0

if __name__ == '__main__':
    main()
