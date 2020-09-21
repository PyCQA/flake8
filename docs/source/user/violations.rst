===================================
 Selecting and Ignoring Violations
===================================

It is possible to select and ignore certain violations reported by |Flake8|
and the plugins we've installed. It's also possible as of |Flake8| 3.0 to
combine usage of :option:`flake8 --select` and :option:`flake8 --ignore`. This
chapter of the User Guide aims to educate about how Flake8 will report errors
based on different inputs.



Ignoring Violations with Flake8
===============================

By default, |Flake8| has a list of error codes that it ignores. The list used
by a version of |Flake8| may be different than the list used by a different
version. To see the default list, :option:`flake8 --help` will
show the output with the current default list.

Extending the Default Ignore List
---------------------------------

If we want to extend the default list of ignored error codes, we can use
:option:`flake8 --extend-ignore` to specify a comma-separated list of codes
for a specific run on the command line, e.g.,

.. prompt:: bash

    flake8 --extend-ignore=E1,E23 path/to/files/ path/to/more/files

This tells |Flake8| to ignore any error codes starting with ``E1`` and ``E23``,
in addition the default ignore list. To view the default error code ignore
list, run :option:`flake8 --help` and refer to the help text for
:option:`flake8 --ignore`.


..
   The section below used to be titled `Changing the Default Ignore List`, but
   was renamed for clarity.
   Explicitly retain the old section anchor so as to not break links:

.. _changing-the-ignore-list:

Overriding the Default Ignore List
----------------------------------

If we want to *completely* override the default list of ignored error codes, we
can use :option:`flake8 --ignore` to specify a comma-separated list of codes
for a specific run on the command-line, e.g.,

.. prompt:: bash

    flake8 --ignore=E1,E23,W503 path/to/files/ path/to/more/files/

This tells |Flake8| to *only* ignore error codes starting with ``E1``, ``E23``,
or ``W503`` while it is running.

.. note::

    The documentation for :option:`flake8 --ignore` shows examples for how
    to change the ignore list in the configuration file. See also
    :ref:`configuration` as well for details about how to use configuration
    files.


In-line Ignoring Errors
-----------------------

In some cases, we might not want to ignore an error code (or class of error
codes) for the entirety of our project. Instead, we might want to ignore the
specific error code on a specific line. Let's take for example a line like

.. code-block:: python

    example = lambda: 'example'

Sometimes we genuinely need something this simple. We could instead define
a function like we normally would. Note, in some contexts this distracts from
what is actually happening. In those cases, we can also do:

.. code-block:: python

    example = lambda: 'example'  # noqa: E731

This will only ignore the error from pycodestyle that checks for lambda
assignments and generates an ``E731``. If there are other errors on the line
then those will be reported. ``# noqa`` is case-insensitive, without the colon
the part after ``# noqa`` would be ignored.

.. note::

    If we ever want to disable |Flake8| respecting ``# noqa`` comments, we can
    refer to :option:`flake8 --disable-noqa`.

If we instead had more than one error that we wished to ignore, we could
list all of the errors with commas separating them:

.. code-block:: python

    # noqa: E731,E123

Finally, if we have a particularly bad line of code, we can ignore every error
using simply ``# noqa`` with nothing after it.

Contents before and after the ``# noqa: ...`` portion are ignored so multiple
comments may appear on one line.  Here are several examples:

.. code-block:: python

    # mypy requires `# type: ignore` to appear first
    x = 5  # type: ignore  # noqa: ABC123

    # can use to add useful user information to a noqa comment
    y = 6  # noqa: ABC456  # TODO: will fix this later


Ignoring Entire Files
---------------------

Imagine a situation where we are adding |Flake8| to a codebase. Let's further
imagine that with the exception of a few particularly bad files, we can add
|Flake8| easily and move on with our lives. There are two ways to ignore the
file:

#. By explicitly adding it to our list of excluded paths (see: :option:`flake8
   --exclude`)

#. By adding ``# flake8: noqa`` to the file

The former is the **recommended** way of ignoring entire files. By using our
exclude list, we can include it in our configuration file and have one central
place to find what files aren't included in |Flake8| checks. The latter has the
benefit that when we run |Flake8| with :option:`flake8 --disable-noqa` all of
the errors in that file will show up without having to modify our
configuration. Both exist so we can choose which is better for us.



Selecting Violations with Flake8
================================

|Flake8| has a default list of violation classes that we use. This list is:

- ``C90``

  All ``C90`` class violations are reported when the user specifies
  :option:`flake8 --max-complexity`

- ``E``

  All ``E`` class violations are "errors" reported by pycodestyle

- ``F``

  All ``F`` class violations are reported by pyflakes

- ``W``

  All ``W`` class violations are "warnings" reported by pycodestyle

This list can be overridden by specifying :option:`flake8 --select`. Just as
specifying :option:`flake8 --ignore` will change the behaviour of |Flake8|, so
will :option:`flake8 --select`.

Let's look through some examples using this sample code:

.. code-block:: python

    # example.py
    def foo():
        print(
                    "Hello"
            "World"
            )

By default, if we run ``flake8`` on this file we'll get:

.. prompt:: bash

    flake8 example.py

.. code:: text

    example.py:4:9: E131 continuation line unaligned for hanging indent

Now let's select all ``E`` class violations:

.. prompt:: bash

    flake8 --select E example.py

.. code:: text

    example.py:3:17: E126 continuation line over-indented for hanging indent
    example.py:4:9: E131 continuation line unaligned for hanging indent
    example.py:5:9: E121 continuation line under-indented for hanging indent

Suddenly we now have far more errors that are reported to us. Using
``--select`` alone will override the default ``--ignore`` list. In these cases,
the user is telling us that they want all ``E`` violations and so we ignore
our list of violations that we ignore by default.

We can also be highly specific. For example, we can do

.. prompt:: bash

    flake8 --select E121 example.py

.. code:: text

    example.py:5:9: E121 continuation line under-indented for hanging indent

We can also specify lists of items to select both on the command-line and in
our configuration files.

.. prompt:: bash

    flake8 --select E121,E131 example.py

.. code:: text

    example.py:4:9: E131 continuation line unaligned for hanging indent
    example.py:5:9: E121 continuation line under-indented for hanging indent



Selecting and Ignoring Simultaneously For Fun and Profit
========================================================

Prior to |Flake8| 3.0, all handling of :option:`flake8 --select` and
:option:`flake8 --ignore` was delegated to pycodestyle. Its handling of the
options significantly differs from how |Flake8| 3.0 has been designed.

pycodestyle has always preferred ``--ignore`` over ``--select`` and will
ignore ``--select`` if the user provides both. |Flake8| 3.0 will now do its
best to intuitively combine both options provided by the user. Let's look at
some examples using:

.. code-block:: python

    # example.py
    import os


    def foo():
        var = 1
        print(
                    "Hello"
            "World"
            )

If we run |Flake8| with its default settings we get:

.. prompt:: bash

    flake8 example.py

.. code:: text

    example.py:1:1: F401 'os' imported but unused
    example.py:5:5: F841 local variable 'var' is assigned to but never used
    example.py:8:9: E131 continuation line unaligned for hanging indent

Now let's select all ``E`` and ``F`` violations including those in the default
ignore list.

.. prompt:: bash

    flake8 --select E,F example.py

.. code:: text

    example.py:1:1: F401 'os' imported but unused
    example.py:5:5: F841 local variable 'var' is assigned to but never used
    example.py:7:17: E126 continuation line over-indented for hanging indent
    example.py:8:9: E131 continuation line unaligned for hanging indent
    example.py:9:9: E121 continuation line under-indented for hanging indent

Now let's selectively ignore some of these while selecting the rest:

.. prompt:: bash

    flake8 --select E,F --ignore F401,E121 example.py

.. code:: text

    example.py:5:5: F841 local variable 'var' is assigned to but never used
    example.py:7:17: E126 continuation line over-indented for hanging indent
    example.py:8:9: E131 continuation line unaligned for hanging indent

Via this example, we can see that the *most specific* **user-specified** rule
will win. So in the above, we had very vague select rules and two very
specific ignore rules. Let's look at a different example:

.. prompt:: bash

    flake8 --select F401,E131 --ignore E,F example.py

.. code:: text

    example.py:1:1: F401 'os' imported but unused
    example.py:8:9: E131 continuation line unaligned for hanging indent

In this case, we see that since our selected violation codes were more
specific those were reported.
