
"""
Implementation of the command-line I{flake8} tool.
"""
import sys
import os

from flake8.util import skip_file
from flake8 import pep8
from flake8 import pyflakes
from flake8 import mccabe


def check_file(path, complexity=10):

    warnings = pyflakes.checkPath(path)
    warnings += pep8.input_file(path)
    warnings += mccabe.get_module_complexity(path, complexity)
    return warnings


def check_code(code, complexity=10):
    warnings = pyflakes.check(code, '<stdin>')
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
    pep8.process_options()
    warnings = 0
    args = sys.argv[1:]
    if args:
        for path in _get_python_files(args):
            warnings += check_file(path)
    else:
        stdin = sys.stdin.read()
        warnings += check_code(stdin)

    raise SystemExit(warnings > 0)


def _get_files(repo, **kwargs):
    for rev in xrange(repo[kwargs['node']], len(repo)):
        for file_ in repo[rev].files():
            if not file_.endswith('.py'):
                continue
            if skip_file(file_):
                continue
            yield file_


def hg_hook(ui, repo, **kwargs):
    pep8.process_options()
    warnings = 0
    for file_ in _get_files(repo, **kwargs):
        warnings += check_file(file_)

    strict = ui.config('flake8', 'strict')
    if strict is None:
        strict = True

    if strict.lower() in ('1', 'true'):
        return warnings

    return 0

if __name__ == '__main__':
    main()
