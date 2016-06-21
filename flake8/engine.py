# -*- coding: utf-8 -*-
import errno
import io
import platform
import re
import sys
import warnings

import pycodestyle as pep8

from flake8 import __version__
from flake8 import callbacks
from flake8.reporter import (multiprocessing, BaseQReport, FileQReport,
                             QueueReport)
from flake8 import util

_flake8_noqa = re.compile(r'\s*# flake8[:=]\s*noqa', re.I).search

EXTRA_EXCLUDE = ['.tox', '.eggs', '*.egg']

pep8.PROJECT_CONFIG = ('.flake8',) + pep8.PROJECT_CONFIG


def _load_entry_point(entry_point, verify_requirements):
    """Based on the version of setuptools load an entry-point correctly.

    setuptools 11.3 deprecated `require=False` in the call to EntryPoint.load.
    To load entry points correctly after that without requiring all
    dependencies be present, the proper way is to call EntryPoint.resolve.

    This function will provide backwards compatibility for older versions of
    setuptools while also ensuring we do the right thing for the future.
    """
    if hasattr(entry_point, 'resolve') and hasattr(entry_point, 'require'):
        if verify_requirements:
            entry_point.require()
        plugin = entry_point.resolve()
    else:
        plugin = entry_point.load(require=verify_requirements)

    return plugin


def _register_extensions():
    """Register all the extensions."""
    extensions = util.OrderedSet()
    extensions.add(('pycodestyle', pep8.__version__))
    parser_hooks = []
    options_hooks = []
    ignored_hooks = []
    try:
        from pkg_resources import iter_entry_points
    except ImportError:
        pass
    else:
        for entry in iter_entry_points('flake8.extension'):
            # Do not verify that the requirements versions are valid
            checker = _load_entry_point(entry, verify_requirements=False)
            pep8.register_check(checker, codes=[entry.name])
            extensions.add((checker.name, checker.version))
            if hasattr(checker, 'add_options'):
                parser_hooks.append(checker.add_options)
            if hasattr(checker, 'parse_options'):
                options_hooks.append(checker.parse_options)
            if getattr(checker, 'off_by_default', False) is True:
                ignored_hooks.append(entry.name)
    return extensions, parser_hooks, options_hooks, ignored_hooks


def get_parser():
    """This returns an instance of optparse.OptionParser with all the
    extensions registered and options set. This wraps ``pep8.get_parser``.
    """
    (extensions, parser_hooks, options_hooks, ignored) = _register_extensions()
    details = ', '.join('%s: %s' % ext for ext in extensions)
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
        parser.config_options.append('jobs')
        parser.add_option('-j', '--jobs', type='string', default='auto',
                          help="number of jobs to run simultaneously, "
                          "or 'auto'. This is ignored on Windows.")

    parser.add_option('--exit-zero', action='store_true',
                      help="exit with code 0 even if there are errors")
    for parser_hook in parser_hooks:
        parser_hook(parser)
    # See comment above regarding why this has to be a callback.
    parser.add_option('--install-hook', default=False, dest='install_hook',
                      help='Install the appropriate hook for this '
                      'repository.', action='callback',
                      callback=callbacks.install_vcs_hook)
    parser.add_option('--output-file', default=None,
                      help='Redirect report to a file.',
                      type='string', nargs=1, action='callback',
                      callback=callbacks.redirect_stdout)
    parser.add_option('--enable-extensions', default='',
                      dest='enable_extensions',
                      help='Enable plugins and extensions that are disabled '
                           'by default',
                      type='string')
    parser.config_options.extend(['output-file', 'enable-extensions'])
    parser.ignored_extensions = ignored
    return parser, options_hooks


class NoQAStyleGuide(pep8.StyleGuide):

    def input_file(self, filename, lines=None, expected=None, line_offset=0):
        """Run all checks on a Python source file."""
        if self.options.verbose:
            print('checking %s' % filename)
        fchecker = self.checker_class(
            filename, lines=lines, options=self.options)
        # Any "flake8: noqa" comments to ignore the entire file?
        if any(_flake8_noqa(line) for line in fchecker.lines):
            return 0
        return fchecker.check_all(expected=expected, line_offset=line_offset)


class StyleGuide(object):
    """A wrapper StyleGuide object for Flake8 usage.

    This allows for OSErrors to be caught in the styleguide and special logic
    to be used to handle those errors.
    """

    # Reasoning for error numbers is in-line below
    serial_retry_errors = set([
        # ENOSPC: Added by sigmavirus24
        # > On some operating systems (OSX), multiprocessing may cause an
        # > ENOSPC error while trying to trying to create a Semaphore.
        # > In those cases, we should replace the customized Queue Report
        # > class with pep8's StandardReport class to ensure users don't run
        # > into this problem.
        # > (See also: https://gitlab.com/pycqa/flake8/issues/74)
        errno.ENOSPC,
        # NOTE(sigmavirus24): When adding to this list, include the reasoning
        # on the lines before the error code and always append your error
        # code. Further, please always add a trailing `,` to reduce the visual
        # noise in diffs.
    ])

    def __init__(self, **kwargs):
        # This allows us to inject a mocked StyleGuide in the tests.
        self._styleguide = kwargs.pop('styleguide', NoQAStyleGuide(**kwargs))

    @property
    def options(self):
        return self._styleguide.options

    @property
    def paths(self):
        return self._styleguide.paths

    def _retry_serial(self, func, *args, **kwargs):
        """This will retry the passed function in serial if necessary.

        In the event that we encounter an OSError with an errno in
        :attr:`serial_retry_errors`, this function will retry this function
        using pep8's default Report class which operates in serial.
        """
        try:
            return func(*args, **kwargs)
        except OSError as oserr:
            if oserr.errno in self.serial_retry_errors:
                self.init_report(pep8.StandardReport)
            else:
                raise
            return func(*args, **kwargs)

    def check_files(self, paths=None):
        return self._retry_serial(self._styleguide.check_files, paths=paths)

    def excluded(self, filename, parent=None):
        return self._styleguide.excluded(filename, parent=parent)

    def init_report(self, reporter=None):
        return self._styleguide.init_report(reporter)

    def input_file(self, filename, lines=None, expected=None, line_offset=0):
        return self._retry_serial(
            self._styleguide.input_file,
            filename=filename,
            lines=lines,
            expected=expected,
            line_offset=line_offset,
        )


def _parse_multi_options(options, split_token=','):
    r"""Split and strip and discard empties.

    Turns the following:

    A,
    B,

    into ["A", "B"].

    Credit: Kristian Glass as contributed to pep8
    """
    if options:
        return [o.strip() for o in options.split(split_token) if o.strip()]
    else:
        return options


def _disable_extensions(parser, options):
    ignored_extensions = set(getattr(parser, 'ignored_extensions', []))
    enabled = set(_parse_multi_options(options.enable_extensions))

    # Remove any of the selected extensions from the extensions ignored by
    # default.
    ignored_extensions -= enabled

    # Whatever is left afterwards should be unioned with options.ignore and
    # options.ignore should be updated with that.
    options.ignore = tuple(ignored_extensions.union(options.ignore))


def get_style_guide(**kwargs):
    """Parse the options and configure the checker. This returns a sub-class
    of ``pep8.StyleGuide``."""
    kwargs['parser'], options_hooks = get_parser()
    styleguide = StyleGuide(**kwargs)
    options = styleguide.options
    _disable_extensions(kwargs['parser'], options)

    if options.exclude and not isinstance(options.exclude, list):
        options.exclude = pep8.normalize_paths(options.exclude)
    elif not options.exclude:
        options.exclude = []

    # Add patterns in EXTRA_EXCLUDE to the list of excluded patterns
    options.exclude.extend(pep8.normalize_paths(EXTRA_EXCLUDE))

    for options_hook in options_hooks:
        options_hook(options)

    if util.warn_when_using_jobs(options):
        if not multiprocessing:
            warnings.warn("The multiprocessing module is not available. "
                          "Ignoring --jobs arguments.")
        if util.is_windows():
            warnings.warn("The --jobs option is not available on Windows. "
                          "Ignoring --jobs arguments.")
        if util.is_using_stdin(styleguide.paths):
            warnings.warn("The --jobs option is not compatible with supplying "
                          "input using - . Ignoring --jobs arguments.")
        if options.diff:
            warnings.warn("The --diff option was specified with --jobs but "
                          "they are not compatible. Ignoring --jobs arguments."
                          )

    if options.diff:
        options.jobs = None

    force_disable_jobs = util.force_disable_jobs(styleguide)

    if multiprocessing and options.jobs and not force_disable_jobs:
        if options.jobs.isdigit():
            n_jobs = int(options.jobs)
        else:
            try:
                n_jobs = multiprocessing.cpu_count()
            except NotImplementedError:
                n_jobs = 1
        if n_jobs > 1:
            options.jobs = n_jobs
            reporter = QueueReport
            if options.quiet:
                reporter = BaseQReport
                if options.quiet == 1:
                    reporter = FileQReport
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


def make_stdin_get_value(original):
    def stdin_get_value():
        if not hasattr(stdin_get_value, 'cached_stdin'):
            value = original()
            if sys.version_info < (3, 0):
                stdin = io.BytesIO(value)
            else:
                stdin = io.StringIO(value)
            stdin_get_value.cached_stdin = stdin
        else:
            stdin = stdin_get_value.cached_stdin
        return stdin.getvalue()

    return stdin_get_value


pep8.stdin_get_value = make_stdin_get_value(pep8.stdin_get_value)
