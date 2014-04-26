# -*- coding: utf-8 -*-
import os
import sys

import setuptools

from flake8.engine import get_parser, get_style_guide
from flake8.util import is_flag, flag_on

if sys.platform.startswith('win'):
    DEFAULT_CONFIG = os.path.expanduser(r'~\.flake8')
else:
    DEFAULT_CONFIG = os.path.join(
        os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'),
        'flake8'
    )

EXTRA_IGNORE = ['.tox']


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

    exit_code = print_report(report, flake8_style)
    raise SystemExit(exit_code > 0)


def print_report(report, flake8_style):
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
            return 1
    return 0


def check_file(path, ignore=(), complexity=-1):
    """Checks a file using pep8 and pyflakes by default and mccabe
    optionally.

    :param str path: path to the file to be checked
    :param tuple ignore: (optional), error and warning codes to be ignored
    :param int complexity: (optional), enables the mccabe check for values > 0
    """
    ignore = set(ignore).union(EXTRA_IGNORE)
    flake8_style = get_style_guide(
        config_file=DEFAULT_CONFIG, ignore=ignore, max_complexity=complexity)
    return flake8_style.input_file(path)


def check_code(code, ignore=(), complexity=-1):
    """Checks code using pep8 and pyflakes by default and mccabe optionally.

    :param str code: code to be checked
    :param tuple ignore: (optional), error and warning codes to be ignored
    :param int complexity: (optional), enables the mccabe check for values > 0
    """
    ignore = set(ignore).union(EXTRA_IGNORE)
    flake8_style = get_style_guide(
        config_file=DEFAULT_CONFIG, ignore=ignore, max_complexity=complexity)
    return flake8_style.input_file(None, lines=code.splitlines(True))


class Flake8Command(setuptools.Command):
    """The :class:`Flake8Command` class is used by setuptools to perform
    checks on registered modules.
    """

    description = "Run flake8 on modules registered in setuptools"
    user_options = []

    def initialize_options(self):
        self.option_to_cmds = {}
        parser = get_parser()[0]
        for opt in parser.option_list:
            cmd_name = opt._long_opts[0][2:]
            option_name = cmd_name.replace('-', '_')
            self.option_to_cmds[option_name] = cmd_name
            setattr(self, option_name, None)

    def finalize_options(self):
        self.options_dict = {}
        for (option_name, cmd_name) in self.option_to_cmds.items():
            if option_name in ['help', 'verbose']:
                continue
            value = getattr(self, option_name)
            if value is None:
                continue
            if is_flag(value):
                value = flag_on(value)
            self.options_dict[option_name] = value

    def distribution_files(self):
        if self.distribution.packages:
            package_dirs = self.distribution.package_dir or {}
            for package in self.distribution.packages:
                pkg_dir = package
                if package in package_dirs:
                    pkg_dir = package_dirs[package]
                elif '' in package_dirs:
                    pkg_dir = package_dirs[''] + os.path.sep + pkg_dir
                yield pkg_dir.replace('.', os.path.sep)

        if self.distribution.py_modules:
            for filename in self.distribution.py_modules:
                yield "%s.py" % filename
        # Don't miss the setup.py file itself
        yield "setup.py"

    def run(self):
        # Prepare
        paths = list(self.distribution_files())
        flake8_style = get_style_guide(config_file=DEFAULT_CONFIG,
                                       paths=paths,
                                       **self.options_dict)

        # Run the checkers
        report = flake8_style.check_files()
        exit_code = print_report(report, flake8_style)
        raise SystemExit(exit_code > 0)
