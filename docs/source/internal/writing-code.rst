.. _writing-code:

=========================
 Writing Code for Flake8
=========================

The maintainers of |Flake8| unsurprisingly have some opinions about the style
of code maintained in the project.

At the time of this writing, |Flake8| enables all of PyCodeStyle's checks, all
of PyFlakes' checks, and sets a maximum complexity value (for McCabe) of 10.
On top of that, we enforce PEP-0257 style doc-strings via PyDocStyle
(disabling only D203) and Google's import order style using
flake8-import-order.

The last two are a little unusual, so we provide examples below.


PEP-0257 style doc-strings
==========================

|Flake8| attempts to document both internal interfaces as well as our API and
doc-strings provide a very convenient way to do so. Even if a function, class,
or method isn't included specifically in our documentation having a doc-string
is still preferred. Further, |Flake8| has some style preferences that are not
checked by PyDocStyle.

For example, while most people will never read the doc-string for
:func:`flake8.main.git.hook` that doc-string still provides value to the
maintainers and future collaborators. They (very explicitly) describe the
purpose of the function, a little of what it does, and what parameters it
accepts as well as what it returns.

.. code-block:: python

    # src/flake8/main/git.py
    def hook(lazy: bool = False, strict: bool = False) -> int:
        """Execute Flake8 on the files in git's index.

        Determine which files are about to be committed and run Flake8 over them
        to check for violations.

        :param lazy:
            Find files not added to the index prior to committing. This is useful
            if you frequently use ``git commit -a`` for example. This defaults to
            False since it will otherwise include files not in the index.
        :param strict:
            If True, return the total number of errors/violations found by Flake8.
            This will cause the hook to fail.
        :returns:
            Total number of errors found during the run.
        """
        # NOTE(sigmavirus24): Delay import of application until we need it.
        from flake8.main import application
        app = application.Application()
        with make_temporary_directory() as tempdir:
            filepaths = list(copy_indexed_files_to(tempdir, lazy))
            app.initialize(['.'])
            app.options.exclude = update_excludes(app.options.exclude, tempdir)
            app.run_checks(filepaths)

        app.report_errors()
        if strict:
            return app.result_count
        return 0

Note that we begin the description of the parameter on a new-line and
indented 4 spaces.

Following the above examples and guidelines should help you write doc-strings
that are stylistically correct for |Flake8|.


Imports
=======

|Flake8| follows the import guidelines that Google published in their Python
Style Guide. In short this includes:

- Only importing modules

- Grouping imports into

  * standard library imports

  * third-party dependency imports

  * local application imports

- Ordering imports alphabetically

In practice this would look something like:

.. code-block:: python

    import configparser
    import logging
    from os import path

    import requests

    from flake8 import exceptions
    from flake8.formatting import base

As a result, of the above, we do not:

- Import objects into a namespace to make them accessible from that namespace

- Import only the objects we're using

- Add comments explaining that an import is a standard library module or
  something else


Other Stylistic Preferences
===========================

Finally, |Flake8| has a few other stylistic preferences that it does not
presently enforce automatically.

Multi-line Function/Method Calls
--------------------------------

When you find yourself having to split a call to a function or method up
across multiple lines, insert a new-line after the opening parenthesis, e.g.,

.. code-block:: python

    # src/flake8/main/options.py
    add_option(
        '-v', '--verbose', default=0, action='count',
        parse_from_config=True,
        help='Print more information about what is happening in flake8.'
             ' This option is repeatable and will increase verbosity each '
             'time it is repeated.',
    )

    # src/flake8/formatting/base.py
    def show_statistics(self, statistics):
        """Format and print the statistics."""
        for error_code in statistics.error_codes():
            stats_for_error_code = statistics.statistics_for(error_code)
            statistic = next(stats_for_error_code)
            count = statistic.count
            count += sum(stat.count for stat in stats_for_error_code)
            self._write(f'{count:<5} {error_code} {statistic.message}')

In the first example, we put a few of the parameters all on one line, and then
added the last two on their own. In the second example, each parameter has its
own line. This particular rule is a little subjective. The general idea is
that putting one parameter per-line is preferred, but sometimes it's
reasonable and understandable to group a few together on one line.

Comments
--------

If you're adding an important comment, be sure to sign it. In |Flake8| we
generally sign comments by preceding them with ``NOTE(<name>)``. For example,

.. code-block:: python

    # NOTE(sigmavirus24): The format strings are a little confusing, even
    # to me, so here's a quick explanation:
    # We specify the named value first followed by a ':' to indicate we're
    # formatting the value.
    # Next we use '<' to indicate we want the value left aligned.
    # Then '10' is the width of the area.
    # For floats, finally, we only want only want at most 3 digits after
    # the decimal point to be displayed. This is the precision and it
    # can not be specified for integers which is why we need two separate
    # format strings.
    float_format = '{value:<10.3} {statistic}'.format
    int_format = '{value:<10} {statistic}'.format

Ian is well known across most websites as ``sigmavirus24`` so he signs his
comments that way.

Verbs Belong in Function Names
------------------------------

|Flake8| prefers that functions have verbs in them. If you're writing a
function that returns a generator of files then ``generate_files`` will always
be preferable to ``make_files`` or ``files``.
