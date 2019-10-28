===================
 Utility Functions
===================

|Flake8| has a few utility functions that it uses internally.

.. warning::

    As should be implied by where these are documented, these are all
    **internal** utility functions. Their signatures and return types
    may change between releases without notice.

    Bugs reported about these **internal** functions will be closed
    immediately.

    If functions are needed by plugin developers, they may be requested
    in the bug tracker and after careful consideration they *may* be added
    to the *documented* stable API.

.. autofunction:: flake8.utils.parse_comma_separated_list

:func:`~flake8.utils.parse_comma_separated_list` takes either a string like

.. code-block:: python

    "E121,W123,F904"
    "E121,\nW123,\nF804"
    " E121,\n\tW123,\n\tF804 "
    " E121\n\tW123 \n\tF804"

And converts it to a list that looks as follows

.. code-block:: python

    ["E121", "W123", "F904"]

This function helps normalize any kind of comma-separated input you or |Flake8|
might receive. This is most helpful when taking advantage of |Flake8|'s
additional parameters to :class:`~flake8.options.manager.Option`.

.. autofunction:: flake8.utils.normalize_path

This utility takes a string that represents a path and returns the absolute
path if the string has a ``/`` in it. It also removes trailing ``/``\ s.

.. autofunction:: flake8.utils.normalize_paths

This function utilizes :func:`~flake8.utils.normalize_path` to normalize a
sequence of paths.  See :func:`~flake8.utils.normalize_path` for what defines a
normalized path.

.. autofunction:: flake8.utils.stdin_get_value

This function retrieves and caches the value provided on ``sys.stdin``. This
allows plugins to use this to retrieve ``stdin`` if necessary.

.. autofunction:: flake8.utils.is_windows

This provides a convenient and explicitly named function that checks if we are
currently running on a Windows (or ``nt``) operating system.

.. autofunction:: flake8.utils.is_using_stdin

Another helpful function that is named only to be explicit given it is a very
trivial check, this checks if the user specified ``-`` in their arguments to
|Flake8| to indicate we should read from stdin.

.. autofunction:: flake8.utils.filenames_from

When provided an argument to |Flake8|, we need to be able to traverse
directories in a convenient manner. For example, if someone runs

.. code::

    $ flake8 flake8/

Then they want us to check all of the files in the directory ``flake8/``. This
function will handle that while also handling the case where they specify a
file like:

.. code::

    $ flake8 flake8/__init__.py


.. autofunction:: flake8.utils.fnmatch

The standard library's :func:`fnmatch.fnmatch` is excellent at deciding if a
filename matches a single pattern. In our use case, however, we typically have
a list of patterns and want to know if the filename matches any of them. This
function abstracts that logic away with a little extra logic.

.. autofunction:: flake8.utils.parameters_for

|Flake8| analyzes the parameters to plugins to determine what input they are
expecting. Plugins may expect one of the following:

- ``physical_line`` to receive the line as it appears in the file

- ``logical_line`` to receive the logical line (not as it appears in the file)

- ``tree`` to receive the abstract syntax tree (AST) for the file

We also analyze the rest of the parameters to provide more detail to the
plugin. This function will return the parameters in a consistent way across
versions of Python and will handle both classes and functions that are used as
plugins. Further, if the plugin is a class, it will strip the ``self``
argument so we can check the parameters of the plugin consistently.

.. autofunction:: flake8.utils.parse_unified_diff

To handle usage of :option:`flake8 --diff`, |Flake8| needs to be able
to parse the name of the files in the diff as well as the ranges indicated the
sections that have been changed. This function either accepts the diff as an
argument or reads the diff from standard-in. It then returns a dictionary with
filenames as the keys and sets of line numbers as the value.
