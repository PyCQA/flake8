==========
Flake8 API
==========

.. module:: flake8

flake8.engine
=============

.. autofunction:: flake8.engine.get_parser

.. autofunction:: flake8.engine.get_style_guide

flake8.hooks
============

.. autofunction:: flake8.hooks.git_hook

.. autofunction:: flake8.hooks.hg_hook

flake8.main
===========

.. autofunction:: flake8.main.main

.. autofunction:: flake8.main.check_file

.. autofunction:: flake8.main.check_code

.. autoclass:: flake8.main.Flake8Command

flake8.util
===========

For AST checkers, this module has the ``iter_child_nodes`` function and 
handles compatibility for all versions of Python between 2.5 and 3.3. The 
function was added to the ``ast`` module in Python 2.6 but is redefined in the 
case where the user is running Python 2.5
