# -*- coding: utf-8 -*-
import re
import platform

import pep8

from flake8 import __version__
from flake8.reporter import multiprocessing, BaseQReport, QueueReport
from flake8.util import OrderedSet

_flake8_noqa = re.compile(r'flake8[:=]\s*noqa', re.I).search


def _register_extensions():
    """Register all the extensions."""
    extensions = OrderedSet()
    extensions.add(('pep8', pep8.__version__))
    parser_hooks = []
    options_hooks = []
    try:
        from pkg_resources import iter_entry_points
    except ImportError:
        pass
    else:
        for entry in iter_entry_points('flake8.extension'):
            checker = entry.load()
            pep8.register_check(checker, codes=[entry.name])
            extensions.add((checker.name, checker.version))
            if hasattr(checker, 'add_options'):
                parser_hooks.append(checker.add_options)
            if hasattr(checker, 'parse_options'):
                options_hooks.append(checker.parse_options)
    return extensions, parser_hooks, options_hooks


def get_parser():
    """This returns an instance of optparse.OptionParser with all the
    extensions registered and options set. This wraps ``pep8.get_parser``.
    """
    (extensions, parser_hooks, options_hooks) = _register_extensions()
    details = ', '.join(['%s: %s' % ext for ext in extensions])
    python_version = get_python_version()
    parser = pep8.get_parser('flake8', '%s (%s) %s' % (
        __version__, details, python_version
    ))
    for opt in ('--repeat', '--testsuite', '--doctest'):
        try:
            parser.remove_option(opt)
        except ValueError:
            pass

    if multiprocessing:
        try:
            auto = multiprocessing.cpu_count() or 1
        except NotImplementedError:
            auto = 1
        parser.config_options.append('jobs')
        parser.add_option('-j', '--jobs', type='string', default='auto',
                          help="number of jobs to run simultaneously, "
                          "or 'auto'")

    parser.add_option('--exit-zero', action='store_true',
                      help="exit with code 0 even if there are errors")
    for parser_hook in parser_hooks:
        parser_hook(parser)
    parser.add_option('--install-hook', default=False, action='store_true',
                      help='Install the appropriate hook for this '
                      'repository.', dest='install_hook')
    return parser, options_hooks


class StyleGuide(pep8.StyleGuide):

    def input_file(self, filename, lines=None, expected=None, line_offset=0):
        """Run all checks on a Python source file."""
        if self.options.verbose:
            print('checking %s' % filename)
        fchecker = self.checker_class(
            filename, lines=lines, options=self.options)
        # Any "# flake8: noqa" line?
        if any(_flake8_noqa(line) for line in fchecker.lines):
            return 0
        return fchecker.check_all(expected=expected, line_offset=line_offset)


def get_style_guide(**kwargs):
    """Parse the options and configure the checker. This returns a sub-class 
    of ``pep8.StyleGuide``."""
    kwargs['parser'], options_hooks = get_parser()
    styleguide = StyleGuide(**kwargs)
    options = styleguide.options
    for options_hook in options_hooks:
        options_hook(options)

    if multiprocessing and options.jobs:
        if options.jobs.isdigit():
            n_jobs = int(options.jobs)
        else:
            try:
                n_jobs = multiprocessing.cpu_count()
            except NotImplementedError:
                n_jobs = 1
        if n_jobs > 1:
            options.jobs = n_jobs
            reporter = BaseQReport if options.quiet else QueueReport
            report = styleguide.init_report(reporter)
            report.input_file = styleguide.input_file
            styleguide.runner = report.task_queue.put

    return styleguide


def get_python_version():
    # The implementation isn't all that important.
    try:
        impl = platform.python_implementation() + " "
    except AttributeError:  # Python 2.5
        impl = ''
    return '%s%s on %s' % (impl, platform.python_version(), platform.system())
