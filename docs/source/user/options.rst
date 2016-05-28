.. _options-list:

================================================
 Full Listing of Options and Their Descriptions
================================================

..
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
                            exclude.(Default:
                            .svn,CVS,.bzr,.hg,.git,__pycache__,.tox)
      --filename=patterns   Only check for filenames matching the patterns in this
                            comma-separated list. (Default: *.py)
      --format=format       Format errors according to the chosen formatter.
      --hang-closing        Hang closing bracket instead of matching indentation
                            of opening bracket's line.
      --ignore=errors       Comma-separated list of errors and warnings to ignore
                            (or skip). For example, ``--ignore=E4,E51,W234``.
                            (Default: E121,E123,E126,E226,E24,E704)
      --max-line-length=n   Maximum allowed line length for the entirety of this
                            run. (Default: 79)
      --select=errors       Comma-separated list of errors and warnings to enable.
                            For example, ``--select=E4,E51,W234``. (Default: )
      --disable-noqa        Disable the effect of "# noqa". This will report
                            errors on lines with "# noqa" at the end.
      --show-source         Show the source generate each error or warning.
      --statistics          Count errors and warnings.
      --enable-extensions=ENABLE_EXTENSIONS
                            Enable plugins and extensions that are otherwise
                            disabled by default
      --exit-zero           Exit with status code "0" even if there are errors.
      -j JOBS, --jobs=JOBS  Number of subprocesses to use to run checks in
                            parallel. This is ignored on Windows. The default,
                            "auto", will auto-detect the number of processors
                            available to use. (Default: auto)
      --output-file=OUTPUT_FILE
                            Redirect report to a file.
      --append-config=APPEND_CONFIG
                            Provide extra config files to parse in addition to the
                            files found by Flake8 by default. These files are the
                            last ones read and so they take the highest precedence
                            when multiple files provide the same option.
      --config=CONFIG       Path to the config file that will be the authoritative
                            config source. This will cause Flake8 to ignore all
                            other configuration files.
      --isolated            Ignore all found configuration files.
      --builtins=BUILTINS   define more built-ins, comma separated
      --doctests            check syntax of the doctests
      --include-in-doctest=INCLUDE_IN_DOCTEST
                            Run doctests only on these files
      --exclude-from-doctest=EXCLUDE_FROM_DOCTEST
                            Skip these files when running doctests

.. option:: --version

    When specified on the command-line, this will show :program:`Flake8`\ 's
    version as well as the versions of all plugins installed.

    **This cannot be specified in the config files.**


.. option:: -h, --help

    When specified on the command-line, this will show a description of how
    to use :program:`Flake8` and it soptions.

    **This cannot be specified in the config files.**

.. option::  -v, --verbose

    When specified on the command-line or in configuration, this will
    increase the verbosity of Flake8's output. Each time you specify
    it, it will print more and more information.

    **This can be specified in the config file.**

    Example config file specification:

    .. code-block:: ini

        verbose = 2
