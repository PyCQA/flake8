
"""
Implementation of the command-line I{flake8} tool.
"""
import sys
import os
import os.path
from subprocess import PIPE, Popen
import select
try:
    from StringIO import StringIO   # NOQA
except ImportError:
    from io import StringIO         # NOQA

from flake8.util import skip_file
from flake8 import pep8
from flake8 import pyflakes
from flake8 import mccabe

pep8style = None


def check_file(path, complexity=-1):
    warnings = pyflakes.checkPath(path)
    warnings += pep8style.input_file(path)
    if complexity > -1:
        warnings += mccabe.get_module_complexity(path, complexity)
    return warnings


def check_code(code, complexity=-1):
    warnings = pyflakes.check(code, 'stdin')
    warnings += pep8style.input_file(StringIO(code))
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
    global pep8style
    pep8style = pep8.StyleGuide(parse_argv=True, config_file=True)
    options = pep8style.options
    complexity = options.max_complexity
    builtins = set(options.builtins)
    warnings = 0

    if builtins:
        orig_builtins = set(pyflakes._MAGIC_GLOBALS)
        pyflakes._MAGIC_GLOBALS = orig_builtins | builtins

    if pep8style.paths and options.filename is not None:
        for path in _get_python_files(pep8style.paths):
            warnings += check_file(path, complexity)
    else:
        # wait for 1 second on the stdin fd
        reads, __, __ = select.select([sys.stdin], [], [], 1.)
        if reads == []:
            print('input not specified')
            raise SystemExit(1)

        stdin = sys.stdin.read()
        warnings += check_code(stdin, complexity)

    if options.exit_zero:
        raise SystemExit(0)
    raise SystemExit(warnings > 0)


def _get_files(repo, **kwargs):
    seen = set()
    for rev in range(repo[kwargs['node']], len(repo)):
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


def _initpep8():
    # default pep8 setup
    pep8.options = _PEP8Options()
    pep8.options.physical_checks = pep8.find_checks('physical_line')
    pep8.options.logical_checks = pep8.find_checks('logical_line')
    pep8.options.counters = dict.fromkeys(pep8.BENCHMARK_KEYS, 0)
    pep8.options.messages = {}
    pep8.options.max_line_length = 79
    pep8.args = []


def run(command):
    p = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    p.wait()
    return (p.returncode, [line.strip() for line in p.stdout.readlines()],
            [line.strip() for line in p.stderr.readlines()])


def git_hook(complexity=-1, strict=False, ignore=None):
    _initpep8()
    if ignore:
        pep8.options.ignore=ignore

    warnings = 0

    _, files_modified, _ = run("git diff-index --cached --name-only HEAD")
    for filename in files_modified:
        ext = os.path.splitext(filename)[-1]
        if ext != '.py':
            continue
        if not os.path.exists(filename):
            continue
        warnings += check_file(filename, complexity)

    if strict:
        return warnings

    return 0


def hg_hook(ui, repo, **kwargs):
    _initpep8()
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
