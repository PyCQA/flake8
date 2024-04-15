.. _options-list:

================================================
 Full Listing of Options and Their Descriptions
================================================

..
    NOTE(sigmavirus24): When adding new options here, please follow the
    following _rough_ template:

    .. option:: --<opt-name>[=<descriptive-name-of-parameter>]

        :ref:`Go back to index <top>`

        Active description of option's purpose (note that each description
        starts with an active verb)

        Command-line usage:

        .. prompt:: bash

            flake8 --<opt-name>[=<example-parameter(s)>] [positional params]

        This **can[ not]** be specified in config files.

        (If it can be, an example using .. code-block:: ini)

    Thank you for your contribution to Flake8's documentation.

.. _top:

Index of Options
================

- :option:`flake8 --version`

- :option:`flake8 --help`

- :option:`flake8 --verbose`

- :option:`flake8 --quiet`

- :option:`flake8 --color`

- :option:`flake8 --count`

- :option:`flake8 --exclude`

- :option:`flake8 --extend-exclude`

- :option:`flake8 --filename`

- :option:`flake8 --stdin-display-name`

- :option:`flake8 --format`

- :option:`flake8 --hang-closing`

- :option:`flake8 --ignore`

- :option:`flake8 --extend-ignore`

- :option:`flake8 --per-file-ignores`

- :option:`flake8 --max-line-length`

- :option:`flake8 --max-doc-length`

- :option:`flake8 --indent-size`

- :option:`flake8 --select`

- :option:`flake8 --extend-select`

- :option:`flake8 --disable-noqa`

- :option:`flake8 --show-source`

- :option:`flake8 --statistics`

- :option:`flake8 --require-plugins`

- :option:`flake8 --enable-extensions`

- :option:`flake8 --exit-zero`

- :option:`flake8 --jobs`

- :option:`flake8 --output-file`

- :option:`flake8 --tee`

- :option:`flake8 --append-config`

- :option:`flake8 --config`

- :option:`flake8 --isolated`

- :option:`flake8 --builtins`

- :option:`flake8 --doctests`

- :option:`flake8 --benchmark`

- :option:`flake8 --bug-report`

- :option:`flake8 --max-complexity`


Options and their Descriptions
==============================

.. program:: flake8

.. option:: --version

    :ref:`Go back to index <top>`

    Show |Flake8|'s version as well as the versions of all plugins
    installed.

    Command-line usage:

    .. prompt:: bash

        flake8 --version

    This **can not** be specified in config files.


.. option:: -h, --help

    :ref:`Go back to index <top>`

    Show a description of how to use |Flake8| and its options.

    Command-line usage:

    .. prompt:: bash

        flake8 --help
        flake8 -h

    This **can not** be specified in config files.


.. option::  -v, --verbose

    :ref:`Go back to index <top>`

    Increase the verbosity of |Flake8|'s output. Each time you specify
    it, it will print more and more information.

    Command-line example:

    .. prompt:: bash

        flake8 -vv

    This **can not** be specified in config files.


.. option:: -q, --quiet

    :ref:`Go back to index <top>`

    Decrease the verbosity of |Flake8|'s output. Each time you specify it,
    it will print less and less information.

    Command-line example:

    .. prompt:: bash

        flake8 -q

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        quiet = 1

.. option:: --color

    :ref:`Go back to index <top>`

    Whether to use color in output. Defaults to ``auto``.

    Possible options are ``auto``, ``always``, and ``never``.

    This **can not** be specified in config files.

    When color is enabled, the following substitutions are enabled:

    - ``%(bold)s``
    - ``%(black)s``
    - ``%(red)s``
    - ``%(green)s``
    - ``%(yellow)s``
    - ``%(blue)s``
    - ``%(magenta)s``
    - ``%(cyan)s``
    - ``%(white)s``
    - ``%(reset)s``


.. option:: --count

    :ref:`Go back to index <top>`

    Print the total number of errors.

    Command-line example:

    .. prompt:: bash

        flake8 --count dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        count = True


.. option:: --exclude=<patterns>

    :ref:`Go back to index <top>`

    Provide a comma-separated list of glob patterns to exclude from checks.

    This defaults to: ``.svn,CVS,.bzr,.hg,.git,__pycache__,.tox,.nox,.eggs,*.egg``

    Example patterns:

    - ``*.pyc`` will match any file that ends with ``.pyc``

    - ``__pycache__`` will match any path that has ``__pycache__`` in it

    - ``lib/python`` will look expand that using :func:`os.path.abspath` and
      look for matching paths

    Command-line example:

    .. prompt:: bash

        flake8 --exclude=*.pyc dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        exclude =
            .tox,
            __pycache__


.. option:: --extend-exclude=<patterns>

    :ref:`Go back to index <top>`

    .. versionadded:: 3.8.0

    Provide a comma-separated list of glob patterns to add to the list of excluded ones.
    Similar considerations as in :option:`--exclude` apply here with regard to the
    value.

    The difference to the :option:`--exclude` option is, that this option can be
    used to selectively add individual patterns without overriding the default
    list entirely.

    Command-line example:

    .. prompt:: bash

        flake8 --extend-exclude=legacy/,vendor/ dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        extend-exclude =
            legacy/,
            vendor/
        extend-exclude = legacy/,vendor/


.. option:: --filename=<patterns>

    :ref:`Go back to index <top>`

    Provide a comma-separate list of glob patterns to include for checks.

    This defaults to: ``*.py``

    Example patterns:

    - ``*.py`` will match any file that ends with ``.py``

    - ``__pycache__`` will match any path that has ``__pycache__`` in it

    - ``lib/python`` will look expand that using :func:`os.path.abspath` and
      look for matching paths

    Command-line example:

    .. prompt:: bash

        flake8 --filename=*.py dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        filename =
            example.py,
            another-example*.py


.. option:: --stdin-display-name=<display_name>

    :ref:`Go back to index <top>`

    Provide the name to use to report warnings and errors from code on stdin.

    Instead of reporting an error as something like:

    .. code::

        stdin:82:73 E501 line too long

    You can specify this option to have it report whatever value you want
    instead of stdin.

    This defaults to: ``stdin``

    Command-line example:

    .. prompt:: bash

        cat file.py | flake8 --stdin-display-name=file.py -

    This **can not** be specified in config files.


.. option:: --format=<format>

    :ref:`Go back to index <top>`

    Select the formatter used to display errors to the user.

    This defaults to: ``default``

    By default, there are two formatters available:

    - default
    - pylint

    Other formatters can be installed. Refer to their documentation for the
    name to use to select them. Further, users can specify their own format
    string. The variables available are:

    - code
    - col
    - path
    - row
    - text

    The default formatter has a format string of:

    .. code-block:: python

        '%(path)s:%(row)d:%(col)d: %(code)s %(text)s'

    Command-line example:

    .. prompt:: bash

        flake8 --format=pylint dir/
        flake8 --format='%(path)s::%(row)d,%(col)d::%(code)s::%(text)s' dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        format=pylint
        format=%(path)s::%(row)d,%(col)d::%(code)s::%(text)s


.. option:: --hang-closing

    :ref:`Go back to index <top>`

    Toggle whether pycodestyle should enforce matching the indentation of the
    opening bracket's line. When you specify this, it will prefer that you
    hang the closing bracket rather than match the indentation.

    Command-line example:

    .. prompt:: bash

        flake8 --hang-closing dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        hang_closing = True
        hang-closing = True


.. option:: --ignore=<errors>

    :ref:`Go back to index <top>`

    Specify a list of codes to ignore. The list is expected to be
    comma-separated, and does not need to specify an error code exactly.
    Since |Flake8| 3.0, this **can** be combined with :option:`--select`. See
    :option:`--select` for more information.

    For example, if you wish to only ignore ``W234``, then you can specify
    that. But if you want to ignore all codes that start with ``W23`` you
    need only specify ``W23`` to ignore them. This also works for ``W2`` and
    ``W`` (for example).

    This defaults to: ``E121,E123,E126,E226,E24,E704,W503,W504``

    Command-line example:

    .. prompt:: bash

        flake8 --ignore=E121,E123 dir/
        flake8 --ignore=E24,E704 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        ignore =
            E121,
            E123
        ignore = E121,E123


.. option:: --extend-ignore=<errors>

    :ref:`Go back to index <top>`

    .. versionadded:: 3.6.0

    Specify a list of codes to add to the list of ignored ones. Similar
    considerations as in :option:`--ignore` apply here with regard to the
    value.

    The difference to the :option:`--ignore` option is, that this option can be
    used to selectively add individual codes without overriding the default
    list entirely.

    Command-line example:

    .. prompt:: bash

        flake8 --extend-ignore=E4,E51,W234 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        extend-ignore =
            E4,
            E51,
            W234
        extend-ignore = E4,E51,W234


.. option:: --per-file-ignores=<filename:errors>[ <filename:errors>]

    :ref:`Go back to index <top>`

    .. versionadded:: 3.7.0

    Specify a list of mappings of files and the codes that should be ignored
    for the entirety of the file. This allows for a project to have a default
    list of violations that should be ignored as well as file-specific
    violations for files that have not been made compliant with the project
    rules.

    This option supports syntax similar to :option:`--exclude` such that glob
    patterns will also work here.

    This can be combined with both :option:`--ignore` and
    :option:`--extend-ignore` to achieve a full flexibility of style options.

    Command-line usage:

    .. prompt:: bash

        flake8 --per-file-ignores='project/__init__.py:F401 setup.py:E121'
        flake8 --per-file-ignores='project/*/__init__.py:F401 setup.py:E121'

    This **can** be specified in config files.

    .. code-block:: ini

        per-file-ignores =
            project/__init__.py:F401
            setup.py:E121
            other_project/*:W9

.. option:: --max-line-length=<n>

    :ref:`Go back to index <top>`

    Set the maximum length that any line (with some exceptions) may be.

    Exceptions include lines that are either strings or comments which are
    entirely URLs. For example:

    .. code-block:: python

        # https://some-super-long-domain-name.com/with/some/very/long/path

        url = '''\
            https://...
        '''

    This defaults to: ``79``

    Command-line example:

    .. prompt:: bash

        flake8 --max-line-length 99 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        max-line-length = 79

.. option:: --max-doc-length=<n>

    :ref:`Go back to index <top>`

    Set the maximum length that a comment or docstring line may be.

    By default, there is no limit on documentation line length.

    Command-line example:

    .. prompt:: bash

        flake8 --max-doc-length 99 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        max-doc-length = 79

.. option:: --indent-size=<n>

    :ref:`Go back to index <top>`

    Set the number of spaces used for indentation.

    By default, 4.

    Command-line example:

    .. prompt:: bash

        flake8 --indent-size 2 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        indent-size = 2

.. option:: --select=<errors>

    :ref:`Go back to index <top>`

    **You usually do not need to specify this option as the default includes
    all installed plugin codes.**

    Specify the list of error codes you wish |Flake8| to report. Similarly to
    :option:`--ignore`. You can specify a portion of an error code to get all
    that start with that string. For example, you can use ``E``, ``E4``,
    ``E43``, and ``E431``.

    Command-line example:

    .. prompt:: bash

        flake8 --select=E431,E5,W,F dir/
        flake8 --select=E,W dir/

    This can also be combined with :option:`--ignore`:

    .. prompt:: bash

        flake8 --select=E --ignore=E432 dir/

    This will report all codes that start with ``E``, but ignore ``E432``
    specifically. This is more flexibly than the |Flake8| 2.x and 1.x used
    to be.

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        select =
            E431,
            W,
            F


.. option:: --extend-select=<errors>

    :ref:`Go back to index <top>`

    .. versionadded:: 4.0.0

    **You usually do not need to specify this option as the default includes
    all installed plugin codes.**

    Specify a list of codes to add to the list of selected ones. Similar
    considerations as in :option:`--select` apply here with regard to the
    value.

    The difference to the :option:`--select` option is, that this option can be
    used to selectively add individual codes without overriding the default
    list entirely.

    Command-line example:

    .. prompt:: bash

        flake8 --extend-select=E4,E51,W234 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        extend-select =
            E4,
            E51,
            W234


.. option:: --disable-noqa

    :ref:`Go back to index <top>`

    Report all errors, even if it is on the same line as a ``# NOQA`` comment.
    ``# NOQA`` can be used to silence messages on specific lines. Sometimes,
    users will want to see what errors are being silenced without editing the
    file. This option allows you to see all the warnings, errors, etc.
    reported.

    Command-line example:

    .. prompt:: bash

        flake8 --disable-noqa dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        disable_noqa = True
        disable-noqa = True


.. option:: --show-source

    :ref:`Go back to index <top>`

    Print the source code generating the error/warning in question.

    Command-line example:

    .. prompt:: bash

        flake8 --show-source dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        show_source = True
        show-source = True


.. option:: --statistics

    :ref:`Go back to index <top>`

    Count the number of occurrences of each error/warning code and
    print a report.

    Command-line example:

    .. prompt:: bash

        flake8 --statistics

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        statistics = True


.. option:: --require-plugins=<names>

    :ref:`Go back to index <top>`

    Require specific plugins to be installed before running.

    This option takes a list of distribution names (usually the name you would
    use when running ``pip install``).

    Command-line example:

    .. prompt:: bash

        flake8 --require-plugins=flake8-2020,flake8-typing-extensions dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        require-plugins =
            flake8-2020
            flake8-typing-extensions


.. _option-enable-extensions:

.. option:: --enable-extensions=<errors>

    :ref:`Go back to index <top>`

    Enable :ref:`off-by-default<off-by-default>` extensions.

    Plugins to |Flake8| have the option of registering themselves as
    off-by-default. These plugins will not be loaded unless enabled by this
    option.

    Command-line example:

    .. prompt:: bash

        flake8 --enable-extensions=H111 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        enable-extensions =
            H111,
            G123
        enable_extensions =
            H111,
            G123


.. option:: --exit-zero

    :ref:`Go back to index <top>`

    Force |Flake8| to use the exit status code 0 even if there are errors.

    By default |Flake8| will exit with a non-zero integer if there are errors.

    Command-line example:

    .. prompt:: bash

        flake8 --exit-zero dir/

    This **can not** be specified in config files.


.. option:: --jobs=<n>

    :ref:`Go back to index <top>`

    Specify the number of subprocesses that |Flake8| will use to run checks in
    parallel.

    .. note::

        This option is ignored on platforms where ``fork`` is not a
        supported ``multiprocessing`` method.

    This defaults to: ``auto``

    The default behaviour will use the number of CPUs on your machine as
    reported by :func:`multiprocessing.cpu_count`.

    Command-line example:

    .. prompt:: bash

        flake8 --jobs=8 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        jobs = 8


.. option:: --output-file=<path>

    :ref:`Go back to index <top>`

    Redirect all output to the specified file.

    Command-line example:

    .. prompt:: bash

        flake8 --output-file=output.txt dir/
        flake8 -vv --output-file=output.txt dir/


.. option:: --tee

    :ref:`Go back to index <top>`

    Also print output to stdout if output-file has been configured.

    Command-line example:

    .. prompt:: bash

        flake8 --tee --output-file=output.txt dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        tee = True


.. option:: --append-config=<config>

    :ref:`Go back to index <top>`

    .. versionadded:: 3.6.0

    Provide extra config files to parse in after and in addition to the files
    that |Flake8| found on its own. Since these files are the last ones read
    into the Configuration Parser, so it has the highest precedence if it
    provides an option specified in another config file.

    Command-line example:

    .. prompt:: bash

        flake8 --append-config=my-extra-config.ini dir/

    This **can not** be specified in config files.


.. option:: --config=<config>

    :ref:`Go back to index <top>`

    Provide a path to a config file that will be the only config file read and
    used. This will cause |Flake8| to ignore all other config files that
    exist.

    Command-line example:

    .. prompt:: bash

        flake8 --config=my-only-config.ini dir/

    This **can not** be specified in config files.


.. option:: --isolated

    :ref:`Go back to index <top>`

    Ignore any config files and use |Flake8| as if there were no config files
    found.

    Command-line example:

    .. prompt:: bash

        flake8 --isolated dir/

    This **can not** be specified in config files.


.. option:: --builtins=<builtins>

    :ref:`Go back to index <top>`

    Provide a custom list of builtin functions, objects, names, etc.

    This allows you to let pyflakes know about builtins that it may
    not immediately recognize so it does not report warnings for using
    an undefined name.

    This is registered by the default PyFlakes plugin.

    Command-line example:

    .. prompt:: bash

        flake8 --builtins=_,_LE,_LW dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        builtins =
            _,
            _LE,
            _LW


.. option:: --doctests

    :ref:`Go back to index <top>`

    Enable PyFlakes syntax checking of doctests in docstrings.

    This is registered by the default PyFlakes plugin.

    Command-line example:

    .. prompt:: bash

        flake8 --doctests dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        doctests = True


.. option:: --benchmark

    :ref:`Go back to index <top>`

    Collect and print benchmarks for this run of |Flake8|. This aggregates the
    total number of:

    - tokens
    - physical lines
    - logical lines
    - files

    and the number of elapsed seconds.

    Command-line usage:

    .. prompt:: bash

        flake8 --benchmark dir/

    This **can not** be specified in config files.


.. option:: --bug-report

    :ref:`Go back to index <top>`

    Generate information necessary to file a complete bug report for Flake8.
    This will pretty-print a JSON blob that should be copied and pasted into a
    bug report for Flake8.

    Command-line usage:

    .. prompt:: bash

        flake8 --bug-report

    The output should look vaguely like:

    .. code-block:: js

        {
          "dependencies": [
            {
              "dependency": "setuptools",
              "version": "25.1.1"
            }
          ],
          "platform": {
            "python_implementation": "CPython",
            "python_version": "2.7.12",
            "system": "Darwin"
          },
          "plugins": [
            {
              "plugin": "mccabe",
              "version": "0.5.1"
            },
            {
              "plugin": "pycodestyle",
              "version": "2.0.0"
            },
            {
              "plugin": "pyflakes",
              "version": "1.2.3"
            }
          ],
          "version": "3.1.0.dev0"
        }

    This **can not** be specified in config files.


.. option:: --max-complexity=<n>

    :ref:`Go back to index <top>`

    Set the maximum allowed McCabe complexity value for a block of code.

    This option is provided by the ``mccabe`` dependency's |Flake8| plugin.

    Command-line usage:

    .. prompt:: bash

        flake8 --max-complexity 15 dir/

    This **can** be specified in config files.

    Example config file usage:

    .. code-block:: ini

        max-complexity = 15
