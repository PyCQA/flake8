.. _error-codes:

Warning / Error codes
=====================

The convention of Flake8 is to assign a code to each error or warning, like
the ``pep8`` tool.  These codes are used to configure the list of errors
which are selected or ignored.

Each code consists of an upper case ASCII letter followed by three digits.
The recommendation is to use a different prefix for each plugin. A list of the
known prefixes is published below:

- ``E***``/``W***``: `pep8 errors and warnings
  <http://pep8.readthedocs.org/en/latest/intro.html#error-codes>`_
- ``F***``: PyFlakes codes (see below)
- ``C9**``: McCabe complexity plugin `mccabe
  <https://github.com/flintwork/mccabe>`_
- ``N8**``: Naming Conventions plugin `pep8-naming
  <https://github.com/flintwork/pep8-naming>`_


The original PyFlakes does not provide error codes.  Flake8 patches the
PyFlakes messages to add the following codes:

+------+--------------------------------------------------------------------+
| code | sample message                                                     |
+======+====================================================================+
| F401 | ``module`` imported but unused                                     |
+------+--------------------------------------------------------------------+
| F402 | import ``module`` from line ``N`` shadowed by loop variable        |
+------+--------------------------------------------------------------------+
| F403 | 'from ``module`` import \*' used; unable to detect undefined names |
+------+--------------------------------------------------------------------+
| F404 | future import(s) ``name`` after other statements                   |
+------+--------------------------------------------------------------------+
+------+--------------------------------------------------------------------+
| F811 | redefinition of unused ``name`` from line ``N``                    |
+------+--------------------------------------------------------------------+
| F812 | list comprehension redefines ``name`` from line ``N``              |
+------+--------------------------------------------------------------------+
| F821 | undefined name ``name``                                            |
+------+--------------------------------------------------------------------+
| F822 | undefined name ``name`` in __all__                                 |
+------+--------------------------------------------------------------------+
| F823 | local variable ``name`` ... referenced before assignment           |
+------+--------------------------------------------------------------------+
| F831 | duplicate argument ``name`` in function definition                 |
+------+--------------------------------------------------------------------+
| F841 | local variable ``name`` is assigned to but never used              |
+------+--------------------------------------------------------------------+
