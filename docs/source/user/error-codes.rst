.. _error_codes:

=========================
 Error / Violation Codes
=========================

Flake8 and its plugins assign a code to each message that we refer to as an
:term:`error code` (or :term:`violation`). Most plugins will list their error
codes in their documentation or README.

Flake8 installs ``pycodestyle``, ``pyflakes``, and ``mccabe`` by default and
generates its own :term:`error code`\ s for ``pyflakes``:

+------+---------------------------------------------------------------------+
| Code | Example Message                                                     |
+======+=====================================================================+
| F401 | ``module`` imported but unused                                      |
+------+---------------------------------------------------------------------+
| F402 | import ``module`` from line ``N`` shadowed by loop variable         |
+------+---------------------------------------------------------------------+
| F403 | 'from ``module`` import \*' used; unable to detect undefined names  |
+------+---------------------------------------------------------------------+
| F404 | future import(s) ``name`` after other statements                    |
+------+---------------------------------------------------------------------+
| F405 | ``name`` may be undefined, or defined from star imports: ``module`` |
+------+---------------------------------------------------------------------+
| F406 | 'from ``module`` import \*' only allowed at module level            |
+------+---------------------------------------------------------------------+
| F407 | an undefined ``__future__`` feature name was imported               |
+------+---------------------------------------------------------------------+
+------+---------------------------------------------------------------------+
| F501 | invalid ``%`` format literal                                        |
+------+---------------------------------------------------------------------+
| F502 | ``%`` format expected mapping but got sequence                      |
+------+---------------------------------------------------------------------+
| F503 | ``%`` format expected sequence but got mapping                      |
+------+---------------------------------------------------------------------+
| F504 | ``%`` format unused named arguments                                 |
+------+---------------------------------------------------------------------+
| F505 | ``%`` format missing named arguments                                |
+------+---------------------------------------------------------------------+
| F506 | ``%`` format mixed positional and named arguments                   |
+------+---------------------------------------------------------------------+
| F507 | ``%`` format mismatch of placeholder and argument count             |
+------+---------------------------------------------------------------------+
| F508 | ``%`` format with ``*`` specifier requires a sequence               |
+------+---------------------------------------------------------------------+
| F509 | ``%`` format with unsupported format character                      |
+------+---------------------------------------------------------------------+
| F521 | ``.format(...)`` invalid format string                              |
+------+---------------------------------------------------------------------+
| F522 | ``.format(...)`` unused named arguments                             |
+------+---------------------------------------------------------------------+
| F523 | ``.format(...)`` unused positional arguments                        |
+------+---------------------------------------------------------------------+
| F524 | ``.format(...)`` missing argument                                   |
+------+---------------------------------------------------------------------+
| F525 | ``.format(...)`` mixing automatic and manual numbering              |
+------+---------------------------------------------------------------------+
| F541 | f-string without any placeholders                                   |
+------+---------------------------------------------------------------------+
+------+---------------------------------------------------------------------+
| F601 | dictionary key ``name`` repeated with different values              |
+------+---------------------------------------------------------------------+
| F602 | dictionary key variable ``name`` repeated with different values     |
+------+---------------------------------------------------------------------+
| F621 | too many expressions in an assignment with star-unpacking           |
+------+---------------------------------------------------------------------+
| F622 | two or more starred expressions in an assignment ``(a, *b, *c = d)``|
+------+---------------------------------------------------------------------+
| F631 | assertion test is a tuple, which is always ``True``                 |
+------+---------------------------------------------------------------------+
| F632 | use ``==/!=`` to compare ``str``, ``bytes``, and ``int`` literals   |
+------+---------------------------------------------------------------------+
| F633 | use of ``>>`` is invalid with ``print`` function                    |
+------+---------------------------------------------------------------------+
| F634 | if test is a tuple, which is always ``True``                        |
+------+---------------------------------------------------------------------+
+------+---------------------------------------------------------------------+
| F701 | a ``break`` statement outside of a ``while`` or ``for`` loop        |
+------+---------------------------------------------------------------------+
| F702 | a ``continue`` statement outside of a ``while`` or ``for`` loop     |
+------+---------------------------------------------------------------------+
| F704 | a ``yield`` or ``yield from`` statement outside of a function       |
+------+---------------------------------------------------------------------+
| F706 | a ``return`` statement outside of a function/method                 |
+------+---------------------------------------------------------------------+
| F707 | an ``except:`` block as not the last exception handler              |
+------+---------------------------------------------------------------------+
| F721 | syntax error in doctest                                             |
+------+---------------------------------------------------------------------+
| F722 | syntax error in forward annotation                                  |
+------+---------------------------------------------------------------------+
| F723 | syntax error in type comment                                        |
+------+---------------------------------------------------------------------+
+------+---------------------------------------------------------------------+
| F811 | redefinition of unused ``name`` from line ``N``                     |
+------+---------------------------------------------------------------------+
| F821 | undefined name ``name``                                             |
+------+---------------------------------------------------------------------+
| F822 | undefined name ``name`` in ``__all__``                              |
+------+---------------------------------------------------------------------+
| F823 | local variable ``name`` ... referenced before assignment            |
+------+---------------------------------------------------------------------+
| F824 | ``global name`` / ``nonlocal name`` is unused: name is never        |
|      | assigned in scope                                                   |
+------+---------------------------------------------------------------------+
| F831 | duplicate argument ``name`` in function definition                  |
+------+---------------------------------------------------------------------+
| F841 | local variable ``name`` is assigned to but never used               |
+------+---------------------------------------------------------------------+
+------+---------------------------------------------------------------------+
| F901 | ``raise NotImplemented`` should be ``raise NotImplementedError``    |
+------+---------------------------------------------------------------------+

We also report one extra error: ``E999``. We report ``E999`` when we fail to
compile a file into an Abstract Syntax Tree for the plugins that require it.

``mccabe`` only ever reports one :term:`violation` - ``C901`` based on the
complexity value provided by the user.

Users should also reference `pycodestyle's list of error codes`_.


.. links
.. _pycodestyle's list of error codes:
    https://pycodestyle.readthedocs.io/en/latest/intro.html#error-codes
