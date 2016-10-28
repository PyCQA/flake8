=========================
 Error / Violation Codes
=========================

Flake8 and its plugins assign a code to each message that we refer to as a
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
+------+---------------------------------------------------------------------+
| F811 | redefinition of unused ``name`` from line ``N``                     |
+------+---------------------------------------------------------------------+
| F812 | list comprehension redefines ``name`` from line ``N``               |
+------+---------------------------------------------------------------------+
| F821 | undefined name ``name``                                             |
+------+---------------------------------------------------------------------+
| F822 | undefined name ``name`` in __all__                                  |
+------+---------------------------------------------------------------------+
| F823 | local variable ``name`` ... referenced before assignment            |
+------+---------------------------------------------------------------------+
| F831 | duplicate argument ``name`` in function definition                  |
+------+---------------------------------------------------------------------+
| F841 | local variable ``name`` is assigned to but never used               |
+------+---------------------------------------------------------------------+

We also report one extra error: ``E999``. We report ``E999`` when we fail to
compile a file into an Abstract Syntax Tree for the plugins that require it.

``mccabe`` only ever reports one :term:`violation` - ``C901`` based on the
complexity value provided by the user.

Users should also reference `pycodestyle's list of error codes`_.


.. links
.. _pycodestyle's list of error codes:
    https://pycodestyle.readthedocs.io/en/latest/intro.html#error-codes
