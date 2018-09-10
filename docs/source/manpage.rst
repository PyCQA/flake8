========
 flake8
========

SYNOPSIS
========

.. code::

    flake8 [options] [<path> <path> ...]

    flake8 --help

DESCRIPTION
===========

``flake8`` is a command-line utility for enforcing style consistency across
Python projects. By default it includes lint checks provided by the PyFlakes
project, PEP-0008 inspired style checks provided by the PyCodeStyle project,
and McCabe complexity checking provided by the McCabe project. It will also
run third-party extensions if they are found and installed.

OPTIONS
=======

It is important to note that third-party extensions may add options which are
not represented here. To see all options available in your installation, run::

    flake8 --help

All options available as of Flake8 3.1.0::

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -v, --verbose         Print more information about what is happening in
                          flake8. This option is repeatable and will increase
                          verbosity each time it is repeated.
    -q, --quiet           Report only file names, or nothing. This option is
                          repeatable.
    --count               Print total number of errors and warnings to standard
                          error and set the exit code to 1 if total is not
                          empty.
    --diff                Report changes only within line number ranges in the
                          unified diff provided on standard in by the user.
    --exclude=patterns    Comma-separated list of files or directories to
                          exclude. (Default:
                          .svn,CVS,.bzr,.hg,.git,__pycache__,.tox,.eggs,*.egg)
    --filename=patterns   Only check for filenames matching the patterns in this
                          comma-separated list. (Default: *.py)
    --stdin-display-name=STDIN_DISPLAY_NAME
                          The name used when reporting errors from code passed
                          via stdin. This is useful for editors piping the file
                          contents to flake8. (Default: stdin)
    --format=format       Format errors according to the chosen formatter.
    --hang-closing        Hang closing bracket instead of matching indentation
                          of opening bracket's line.
    --ignore=errors       Comma-separated list of errors and warnings to ignore
                          (or skip). For example, ``--ignore=E4,E51,W234``.
                          (Default: E121,E123,E126,E226,E24,E704,W503,W504)
    --max-line-length=n   Maximum allowed line length for the entirety of this
                          run. (Default: 79)
    --select=errors       Comma-separated list of errors and warnings to enable.
                          For example, ``--select=E4,E51,W234``. (Default:
                          E,F,W,C90)
    --disable-noqa        Disable the effect of "# noqa". This will report
                          errors on lines with "# noqa" at the end.
    --show-source         Show the source generate each error or warning.
    --statistics          Count errors and warnings.
    --enable-extensions=ENABLE_EXTENSIONS
                          Enable plugins and extensions that are otherwise
                          disabled by default
    --exit-zero           Exit with status code "0" even if there are errors.
    --install-hook=INSTALL_HOOK
                          Install a hook that is run prior to a commit for the
                          supported version control system.
    -j JOBS, --jobs=JOBS  Number of subprocesses to use to run checks in
                          parallel. This is ignored on Windows. The default,
                          "auto", will auto-detect the number of processors
                          available to use. (Default: auto)
    --output-file=OUTPUT_FILE
                          Redirect report to a file.
    --tee                 Write to stdout and output-file.
    --append-config=APPEND_CONFIG
                          Provide extra config files to parse in addition to the
                          files found by Flake8 by default. These files are the
                          last ones read and so they take the highest precedence
                          when multiple files provide the same option.
    --config=CONFIG       Path to the config file that will be the authoritative
                          config source. This will cause Flake8 to ignore all
                          other configuration files.
    --isolated            Ignore all configuration files.
    --benchmark           Print benchmark information about this run of Flake8
    --bug-report          Print information necessary when preparing a bug
                          report
    --builtins=BUILTINS   define more built-ins, comma separated
    --doctests            check syntax of the doctests
    --include-in-doctest=INCLUDE_IN_DOCTEST
                          Run doctests only on these files
    --exclude-from-doctest=EXCLUDE_FROM_DOCTEST
                          Skip these files when running doctests
    --max-complexity=MAX_COMPLEXITY
                          McCabe complexity threshold

EXAMPLES
========

Simply running flake8 against the current directory::

    flake8
    flake8 .

Running flake8 against a specific path::

    flake8 path/to/file.py

Ignoring violations from flake8::

    flake8 --ignore E101
    flake8 --ignore E1,E202

Only report certain violations::

    flake8 --select E101
    flake8 --select E2,E742

Analyzing only a diff::

    git diff -U0 | flake8 --diff -

Generate information for a bug report::

    flake8 --bug-report

SEE ALSO
========

Flake8 documentation: http://flake8.pycqa.org

Flake8 Options and Examples: http://flake8.pycqa.org/en/latest/user/options.html

PyCodeStyle documentation: http://pycodestyle.pycqa.org

PyFlakes: https://github.com/pycqa/pyflakes

McCabe: https://github.com/pycqa/mccabe

BUGS
====

Please report all bugs to https://gitlab.com/pycqa/flake8
