.. _invocation:

=================
 Invoking Flake8
=================

Once you have :ref:`installed <installation-guide>` |Flake8|, you can begin
using it. Most of the time, you will be able to generically invoke |Flake8|
like so:

.. prompt:: bash

    flake8 ...

Where you simply allow the shell running in your terminal to locate |Flake8|.
In some cases, though, you may have installed |Flake8| for multiple versions
of Python (e.g., Python 3.8 and Python 3.9) and you need to call a specific
version. In that case, you will have much better results using:

.. prompt:: bash

    python3.8 -m flake8

Or

.. prompt:: bash

    python3.9 -m flake8

Since that will tell the correct version of Python to run |Flake8|.

.. note::

    Installing |Flake8| once will not install it on both Python 3.8 and
    Python 3.9. It will only install it for the version of Python that
    is running pip.

It is also possible to specify command-line options directly to |Flake8|:

.. prompt:: bash

    flake8 --select E123

Or

.. prompt:: bash

    python<version> -m flake8 --select E123

.. note::

    This is the last time we will show both versions of an invocation.
    From now on, we'll simply use ``flake8`` and assume that the user
    knows they can instead use ``python<version> -m flake8`` instead.

It's also possible to narrow what |Flake8| will try to check by specifying
exactly the paths and directories you want it to check. Let's assume that
we have a directory with python files and sub-directories which have python
files (and may have more sub-directories) called ``my_project``. Then if
we only want errors from files found inside ``my_project`` we can do:

.. prompt:: bash

    flake8 my_project

And if we only want certain errors (e.g., ``E123``) from files in that
directory we can also do:

.. prompt:: bash

    flake8 --select E123 my_project

If you want to explore more options that can be passed on the command-line,
you can use the ``--help`` option:

.. prompt:: bash

    flake8 --help

And you should see something like:

.. code::

    Usage: flake8 [options] file file ...

    Options:
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
                            exclude.(Default:
                            .svn,CVS,.bzr,.hg,.git,__pycache__,.tox,.nox,.eggs,
                            *.egg)
      --filename=patterns   Only check for filenames matching the patterns in this
                            comma-separated list. (Default: *.py)
      --format=format       Format errors according to the chosen formatter.
      --hang-closing        Hang closing bracket instead of matching indentation
                            of opening bracket's line.
      --ignore=errors       Comma-separated list of errors and warnings to ignore
                            (or skip). For example, ``--ignore=E4,E51,W234``.
                            (Default: E121,E123,E126,E226,E24,E704)
      --extend-ignore=errors
                            Comma-separated list of errors and warnings to add to
                            the list of ignored ones. For example, ``--extend-
                            ignore=E4,E51,W234``.
      --max-line-length=n   Maximum allowed line length for the entirety of this
                            run. (Default: 79)
      --select=errors       Comma-separated list of errors and warnings to enable.
                            For example, ``--select=E4,E51,W234``. (Default: )
      --extend-select errors
                            Comma-separated list of errors and warnings to add to
                            the list of selected ones. For example, ``--extend-
                            select=E4,E51,W234``.
      --disable-noqa        Disable the effect of "# noqa". This will report
                            errors on lines with "# noqa" at the end.
      --show-source         Show the source generate each error or warning.
      --statistics          Count errors and warnings.
      --enabled-extensions=ENABLED_EXTENSIONS
                            Enable plugins and extensions that are otherwise
                            disabled by default
      --exit-zero           Exit with status code "0" even if there are errors.
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
      --builtins=BUILTINS   define more built-ins, comma separated
      --doctests            check syntax of the doctests
      --include-in-doctest=INCLUDE_IN_DOCTEST
                            Run doctests only on these files
      --exclude-from-doctest=EXCLUDE_FROM_DOCTEST
                            Skip these files when running doctests

    Installed plugins: pyflakes: 1.0.0, pep8: 1.7.0
