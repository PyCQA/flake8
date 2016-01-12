"""Command-line implementation of flake8."""
from flake8 import defaults


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
        '--format', metavar='format', default='default', choices=['default'],
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
