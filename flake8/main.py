import os
import sys
import pep8
import pyflakes.api
import pyflakes.checker
import select
from flake8 import mccabe
from flake8.util import (_initpep8, skip_file, get_parser, read_config,
                         Flake8Reporter)

pep8style = None


def main():
    global pep8style
    # parse out our flags so pep8 doesn't get confused
    parser = get_parser()

    # We then have to re-parse argv to make sure pep8 is properly initialized
    pep8style = pep8.StyleGuide(parse_argv=True, config_file=True,
                                parser=parser)
    opts = pep8style.options

    if opts.install_hook:
        from flake8.hooks import install_hook
        install_hook()

    read_config(opts, parser)

    warnings = 0
    stdin = None

    complexity = opts.max_complexity
    builtins = set(opts.builtins.split(','))
    if builtins:
        orig_builtins = set(pyflakes.checker._MAGIC_GLOBALS)
        pyflakes.checker._MAGIC_GLOBALS = orig_builtins | builtins

    # This is needed so we can ignore some items
    pyflakes_reporter = Flake8Reporter(opts.ignore)

    if pep8style.paths and opts.filename is not None:
        for path in _get_python_files(pep8style.paths):
            if path == '-':
                if stdin is None:
                    stdin = read_stdin()
                warnings += check_code(stdin, opts.ignore, complexity)
            else:
                warnings += check_file(path, opts.ignore, complexity,
                                       pyflakes_reporter)
    else:
        stdin = read_stdin()
        warnings += check_code(stdin, opts.ignore, complexity,
                               pyflakes_reporter)

    if opts.exit_zero:
        raise SystemExit(0)

    raise SystemExit(warnings)


def check_file(path, ignore=(), complexity=-1, reporter=None):
    if pep8style.excluded(path):
        return 0
    warnings = pyflakes.api.checkPath(path, reporter)
    warnings += pep8style.input_file(path)
    if complexity > -1:
        warnings += mccabe.get_module_complexity(path, complexity)
    return warnings


def check_code(code, ignore=(), complexity=-1, reporter=None):
    warnings = pyflakes.api.check(code, '<stdin>', reporter)
    warnings += pep8style.input_file('-', lines=code.split('\n'))
    if complexity > -1:
        warnings += mccabe.get_code_complexity(code, complexity)
    return warnings


def read_stdin():
    # wait for 1 second on the stdin fd
    reads, __, __ = select.select([sys.stdin], [], [], 1.)
    if reads == []:
        print('input not specified')
        raise SystemExit(1)

    return sys.stdin.read()


try:
    from setuptools import Command
except ImportError:
    Flake8Command = None
else:
    class Flake8Command(Command):
        description = "Run flake8 on modules registered in setuptools"
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def distribution_files(self):
            if self.distribution.packages:
                for package in self.distribution.packages:
                    yield package.replace(".", os.path.sep)

            if self.distribution.py_modules:
                for filename in self.distribution.py_modules:
                    yield "%s.py" % filename

        def run(self):
            _initpep8()

            # _get_python_files can produce the same file several
            # times, if one of its paths is a parent of another. Keep
            # a set of checked files to de-duplicate.
            checked = set()

            warnings = 0
            for path in _get_python_files(self.distribution_files()):
                if path not in checked:
                    warnings += check_file(path)
                checked.add(path)

            raise SystemExit(warnings > 0)


def _get_python_files(paths):
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                if pep8style.excluded(dirpath):
                    dirnames[:] = []
                    continue
                for filename in filenames:
                    if not filename.endswith('.py'):
                        continue
                    fullpath = os.path.join(dirpath, filename)
                    if not skip_file(fullpath) or pep8style.excluded(fullpath):
                        yield fullpath

        else:
            if not skip_file(path) or pep8style.excluded(path):
                yield path
