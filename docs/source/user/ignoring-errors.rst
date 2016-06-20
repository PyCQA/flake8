=============================
 Ignoring Errors with Flake8
=============================

By default, |Flake8| has a list of error codes that it ignores. The list used
by a version of |Flake8| may be different than the list used by a different
version. To see the default list, :option:`flake8 --help` will
show the output with the current default list.


Changing the Ignore List
========================

If we want to change the list of ignored codes for a single run, we can use
:option:`flake8 --ignore` to specify a comma-separated list of codes for a
specific run on the command-line, e.g.,

.. prompt:: bash

    flake8 --ignore=E1,E23,W503 path/to/files/ path/to/more/files/

This tells |Flake8| to ignore any error codes starting with ``E1``, ``E23``,
or ``W503`` while it is running.

.. note::

    The documentation for :option:`flake8 --ignore` shows examples for how
    to change the ignore list in the configuration file. See also
    :ref:`configuration` as well for details about how to use configuration
    files.


In-line Ignoring Errors
=======================

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
then those will be reported.

.. note::

    If we ever want to disable |Flake8| respecting ``# noqa`` comments, we can
    can refer to :option:`flake8 --disable-noqa`.

If we instead had more than one error that we wished to ignore, we could
list all of the errors with commas separating them:

.. code-block:: python

    # noqa: E731,E123

Finally, if we have a particularly bad line of code, we can ignore every error
using simply ``# noqa`` with nothing after it.


Ignoring Entire Files
=====================

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
