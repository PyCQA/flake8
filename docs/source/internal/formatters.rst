=====================
 Built-in Formatters
=====================

By default |Flake8| has two formatters built-in, ``default`` and ``pylint``.
These correspond to two classes |DefaultFormatter| and |PylintFormatter|.

In |Flake8| 2.0, pep8 handled formatting of errors and also allowed users to
specify an arbitrary format string as a parameter to ``--format``. In order
to allow for this backwards compatibility, |Flake8| 3.0 made two choices:

#. To not limit a user's choices for ``--format`` to the format class names

#. To make the default formatter attempt to use the string provided by the
   user if it cannot find a formatter with that name.

Default Formatter
=================

The |DefaultFormatter| continues to use the same default format string as
pep8: ``'%(path)s:%(row)d:%(col)d: %(code)s %(text)s'``.

To provide the default functionality it overrides two methods:

#. ``after_init``

#. ``format``

The former allows us to inspect the value provided to ``--format`` by the
user and alter our own format based on that value. The second simply uses
that format string to format the error.

.. autoclass:: flake8.formatting.default.Default
    :members:

Pylint Formatter
================

The |PylintFormatter| simply defines the default Pylint format string from
pep8: ``'%(path)s:%(row)d: [%(code)s] %(text)s'``.

.. autoclass:: flake8.formatting.default.Pylint
    :members:


.. |DefaultFormatter| replace:: :class:`~flake8.formatting.default.Default`
.. |PylintFormatter| replace:: :class:`~flake8.formatting.default.Pylint`
