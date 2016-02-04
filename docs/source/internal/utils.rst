===================
 Utility Functions
===================

Flake8 has a few utility functions that it uses and provides to plugins.

.. autofunction:: flake8.utils.parse_comma_separated_list

:func:`~flake8.utils.parse_comma_separated_list` takes either a string like

.. code-block:: python

    "E121,W123,F904"
    "E121,\nW123,\nF804"
    "E121,\n\tW123,\n\tF804"

Or it will take a list of strings (potentially with whitespace) such as

.. code-block:: python

    ["   E121\n", "\t\nW123   ", "\n\tF904\n    "]

And converts it to a list that looks as follows

.. code-block:: python

    ["E121", "W123", "F904"]

This function helps normalize any kind of comma-separated input you or Flake8
might receive. This is most helpful when taking advantage of Flake8's
additional parameters to :class:`~flake8.options.manager.Option`.

.. autofunction:: flake8.utils.normalize_path

This utility takes a string that represents a path and returns the absolute
path if the string has a ``/`` in it. It also removes trailing ``/``\ s.

.. autofunction:: flake8.utils.normalize_paths

This function utilizes :func:`~flake8.utils.parse_comma_separated_list` and
:func:`~flake8.utils.normalize_path` to normalize it's input to a list of
strings that should be paths.

.. autofunction:: flake8.utils.stdin_get_value

This function retrieves and caches the value provided on ``sys.stdin``. This
allows plugins to use this to retrieve ``stdin`` if necessary.
