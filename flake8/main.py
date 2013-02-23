# -*- coding: utf-8 -*-
import os
import sys

import setuptools

from flake8.engine import get_style_guide

if sys.platform.startswith('win'):
    DEFAULT_CONFIG = os.path.expanduser(r'~\.flake8')
else:
    DEFAULT_CONFIG = os.path.join(
        os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'),
        'flake8'
    )


def main():
    """Parse options and run checks on Python source."""
    # Prepare
    flake8_style = get_style_guide(parse_argv=True, config_file=DEFAULT_CONFIG)
    options = flake8_style.options

    if options.install_hook:
        from flake8.hooks import install_hook
        install_hook()

    # Run the checkers
    report = flake8_style.check_files()

    # Print the final report
    options = flake8_style.options
    if options.statistics:
        report.print_statistics()
    if options.benchmark:
        report.print_benchmark()
    if report.total_errors:
        if options.count:
            sys.stderr.write(str(report.total_errors) + '\n')
        if not options.exit_zero:
            raise SystemExit(1)


def check_file(path, ignore=(), complexity=-1):
    """Checks a file using pep8 and pyflakes by default and mccabe 
    optionally.

    :param str path: path to the file to be checked
    :param tuple ignore: (optional), error and warning codes to be ignored
    :param int complexity: (optional), enables the mccabe check for values > 0
    """
    flake8_style = get_style_guide(
        config_file=DEFAULT_CONFIG, ignore=ignore, max_complexity=complexity)
    return flake8_style.input_file(path)


def check_code(code, ignore=(), complexity=-1):
    """Checks code using pep8 and pyflakes by default and mccabe optionally.

    :param str code: code to be checked
    :param tuple ignore: (optional), error and warning codes to be ignored
    :param int complexity: (optional), enables the mccabe check for values > 0
    """
    flake8_style = get_style_guide(
        config_file=DEFAULT_CONFIG, ignore=ignore, max_complexity=complexity)
    return flake8_style.input_file('-', lines=code.splitlines())


class Flake8Command(setuptools.Command):
    """The :class:`Flake8Command` class is used by setuptools to perform
    checks on registered modules.
    """

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
        flake8_style = get_style_guide(config_file=DEFAULT_CONFIG)
        paths = self.distribution_files()
        report = flake8_style.check_files(paths)
        raise SystemExit(report.total_errors > 0)
