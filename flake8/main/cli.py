"""Command-line implementation of flake8."""
import logging

import flake8
from flake8 import checker
from flake8 import defaults
from flake8 import style_guide
from flake8.options import aggregator
from flake8.options import manager
from flake8.plugins import manager as plugin_manager

LOG = logging.getLogger(__name__)


def register_default_options(option_manager):
    """Register the default options on our OptionManager."""
    add_option = option_manager.add_option

    # pep8 options
    add_option(
        '-v', '--verbose', default=0, action='count',
        parse_from_config=True,
        help='Print more information about what is happening in flake8.'
             ' This option is repeatable and will increase verbosity each '
             'time it is repeated.',
    )
    add_option(
        '-q', '--quiet', default=0, action='count',
        parse_from_config=True,
        help='Report only file names, or nothing. This option is repeatable.',
    )

    add_option(
        '--count', action='store_true', parse_from_config=True,
        help='Print total number of errors and warnings to standard error and'
             ' set the exit code to 1 if total is not empty.',
    )

    add_option(
        '--diff', action='store_true',
        help='Report changes only within line number ranges in the unified '
             'diff provided on standard in by the user.',
    )

    add_option(
        '--exclude', metavar='patterns', default=defaults.EXCLUDE,
        comma_separated_list=True, parse_from_config=True,
        normalize_paths=True,
        help='Comma-separated list of files or directories to exclude.'
             '(Default: %default)',
    )

    add_option(
        '--filename', metavar='patterns', default='*.py',
        parse_from_config=True, comma_separated_list=True,
        help='Only check for filenames matching the patterns in this comma-'
             'separated list. (Default: %default)',
    )

    # TODO(sigmavirus24): Figure out --first/--repeat

    add_option(
        '--format', metavar='format', default='default',
        parse_from_config=True,
        help='Format errors according to the chosen formatter.',
    )

    add_option(
        '--hang-closing', action='store_true', parse_from_config=True,
        help='Hang closing bracket instead of matching indentation of opening'
             " bracket's line.",
    )

    add_option(
        '--ignore', metavar='errors', default=defaults.IGNORE,
        parse_from_config=True, comma_separated_list=True,
        help='Comma-separated list of errors and warnings to ignore (or skip).'
             ' For example, ``--ignore=E4,E51,W234``. (Default: %default)',
    )

    add_option(
        '--max-line-length', type='int', metavar='n',
        default=defaults.MAX_LINE_LENGTH, parse_from_config=True,
        help='Maximum allowed line length for the entirety of this run. '
             '(Default: %default)',
    )

    add_option(
        '--select', metavar='errors', default='',
        parse_from_config=True, comma_separated_list=True,
        help='Comma-separated list of errors and warnings to enable.'
             ' For example, ``--select=E4,E51,W234``. (Default: %default)',
    )

    add_option(
        '--disable-noqa', default=False, parse_from_config=True,
        action='store_true',
        help='Disable the effect of "# noqa". This will report errors on '
             'lines with "# noqa" at the end.'
    )

    # TODO(sigmavirus24): Decide what to do about --show-pep8

    add_option(
        '--show-source', action='store_true', parse_from_config=True,
        help='Show the source generate each error or warning.',
    )

    add_option(
        '--statistics', action='store_true', parse_from_config=True,
        help='Count errors and warnings.',
    )

    # Flake8 options
    add_option(
        '--enabled-extensions', default='', parse_from_config=True,
        comma_separated_list=True, type='string',
        help='Enable plugins and extensions that are otherwise disabled '
             'by default',
    )

    add_option(
        '--exit-zero', action='store_true',
        help='Exit with status code "0" even if there are errors.',
    )

    add_option(
        '-j', '--jobs', type='string', default='auto', parse_from_config=True,
        help='Number of subprocesses to use to run checks in parallel. '
             'This is ignored on Windows. The default, "auto", will '
             'auto-detect the number of processors available to use.'
             ' (Default: %default)',
    )

    add_option(
        '--output-file', default=None, type='string', parse_from_config=True,
        # callback=callbacks.redirect_stdout,
        help='Redirect report to a file.',
    )

    # Config file options

    add_option(
        '--append-config', action='append',
        help='Provide extra config files to parse in addition to the files '
             'found by Flake8 by default. These files are the last ones read '
             'and so they take the highest precedence when multiple files '
             'provide the same option.',
    )

    add_option(
        '--config', default=None,
        help='Path to the config file that will be the authoritative config '
             'source. This will cause Flake8 to ignore all other '
             'configuration files.'
    )

    add_option(
        '--isolated', default=False, action='store_true',
        help='Ignore all found configuration files.',
    )


class Application(object):
    """Abstract our application into a class."""

    def __init__(self, program='flake8', version=flake8.__version__):
        # type: (str, str) -> NoneType
        """Initialize our application.

        :param str program:
            The name of the program/application that we're executing.
        :param str version:
            The version of the program/application we're executing.
        """
        self.program = program
        self.version = version
        self.option_manager = manager.OptionManager(
            prog='flake8', version=flake8.__version__
        )
        register_default_options(self.option_manager)

        # Set the verbosity of the program
        preliminary_opts, _ = self.option_manager.parse_args()
        flake8.configure_logging(preliminary_opts.verbose,
                                 preliminary_opts.output_file)

        self.check_plugins = None
        self.listening_plugins = None
        self.formatting_plugins = None
        self.formatter = None
        self.listener_trie = None
        self.guide = None
        self.file_checker_manager = None

        self.options = None
        self.args = None
        self.result_count = 0

    def find_plugins(self):
        # type: () -> NoneType
        """Find and load the plugins for this application."""
        if self.check_plugins is None:
            self.check_plugins = plugin_manager.Checkers()

        if self.listening_plugins is None:
            self.listening_plugins = plugin_manager.Listeners()

        if self.formatting_plugins is None:
            self.formatting_plugins = plugin_manager.ReportFormatters()

    def register_plugin_options(self):
        # type: () -> NoneType
        """Register options provided by plugins to our option manager."""
        self.check_plugins.register_options(self.option_manager)
        self.listening_plugins.register_options(self.option_manager)
        self.formatting_plugins.register_options(self.option_manager)

    def parse_configuration_and_cli(self, argv=None):
        # type: (Union[NoneType, List[str]]) -> NoneType
        """Parse configuration files and the CLI options.

        :param list argv:
            Command-line arguments passed in directly.
        """
        if self.options is None and self.args is None:
            self.options, self.args = aggregator.aggregate_options(
                self.option_manager, argv
            )

        self.check_plugins.provide_options(self.option_manager, self.options,
                                           self.args)

    def make_formatter(self):
        # type: () -> NoneType
        """Initialize a formatter based on the parsed options."""
        if self.formatter is None:
            self.formatter = self.formatting_plugins.get(
                self.options.format, self.formatting_plugins['default']
            ).execute(self.options)

    def make_notifier(self):
        # type: () -> NoneType
        """Initialize our listener Notifier."""
        if self.listener_trie is None:
            self.listener_trie = self.listening_plugins.build_notifier()

    def make_guide(self):
        # type: () -> NoneType
        """Initialize our StyleGuide."""
        if self.guide is None:
            self.guide = style_guide.StyleGuide(
                self.options, self.listener_trie, self.formatter
            )

    def make_file_checker_manager(self):
        # type: () -> NoneType
        """Initialize our FileChecker Manager."""
        if self.file_checker_manager is None:
            self.file_checker_manager = checker.Manager(
                style_guide=self.guide,
                arguments=self.args,
                checker_plugins=self.check_plugins,
            )

    def run_checks(self):
        # type: () -> NoneType
        """Run the actual checks with the FileChecker Manager."""
        self.file_checker_manager.start()
        self.file_checker_manager.run()
        LOG.info('Finished running')
        self.file_checker_manager.stop()

    def report_errors(self):
        # type: () -> NoneType
        """Report all the errors found by flake8 3.0."""
        LOG.info('Reporting errors')
        self.result_count = self.file_checker_manager.report()

    def _run(self, argv):
        self.find_plugins()
        self.register_plugin_options()
        self.parse_configuration_and_cli(argv)
        self.make_formatter()
        self.make_notifier()
        self.make_guide()
        self.make_file_checker_manager()
        self.run_checks()
        self.report_errors()

    def run(self, argv=None):
        # type: (Union[NoneType, List[str]]) -> NoneType
        """Run our application.

        This method will also handle KeyboardInterrupt exceptions for the
        entirety of the flake8 application. If it sees a KeyboardInterrupt it
        will forcibly clean up the :class:`~flake8.checker.Manager`.
        """
        try:
            self._run(argv)
        except KeyboardInterrupt as exc:
            LOG.critical('Caught keyboard interrupt from user')
            LOG.exception(exc)
            self.file_checker_manager._force_cleanup()


def main(argv=None):
    # type: (Union[NoneType, List[str]]) -> NoneType
    """Main entry-point for the flake8 command-line tool."""
    app = Application()
    app.run(argv)
    raise SystemExit(app.result_count > 0)
