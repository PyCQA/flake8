Writing an Extension for Flake8
===============================

Since Flake8 is now adding support for extensions, we require ``setuptools``
so we can manage extensions through entry points. If you are making an
existing tool compatible with Flake8 but do not already require
``setuptools``, you should probably add it to your list of requirements. Next,
you'll need to edit your ``setup.py`` file so that upon installation, your
extension is registered. If you define a class called ``PackageEntryClass``
then this would look something like the following::


    setup(
        # ...
        entry_points={
            'flake8.extension': ['P10 = package.PackageEntryClass'],
        }
        # ...
    )


If you intend to publish your extension, choose a unique code prefix
following the convention for :ref:`error codes <error-codes>`.
In addition, you can open a request in the `issue tracker
<https://bitbucket.org/tarek/flake8/issues>`_ to register the prefix in the
documentation.

.. TODO: describe the API required for the 3 kind of extensions:
   * physical line checkers
   * logical line checkers
   * AST checkers


A real example: McCabe
----------------------

Below is an example from mccabe_ for how to write your ``setup.py`` file for
your Flake8 extension.

.. code-block:: python

    # https://github.com/flintwork/mccabe/blob/0.2/setup.py#L38:L42
    # -*- coding: utf-8 -*-
    from setuptools import setup

    # ...

    setup(
        name='mccabe',

        # ...

        install_requires=[
            'setuptools',
        ],
        entry_points={
            'flake8.extension': [
                'C90 = mccabe:McCabeChecker',
            ],
        },

        # ...

    )

In ``mccabe.py`` you can see that extra options are added to the parser when
flake8 registers the extension:

.. code-block:: python

    # https://github.com/flintwork/mccabe/blob/0.2/mccabe.py#L225:L254
    class McCabeChecker(object):
        """McCabe cyclomatic complexity checker."""
        name = 'mccabe'
        version = __version__
        _code = 'C901'
        _error_tmpl = "C901 %r is too complex (%d)"
        max_complexity = 0

        def __init__(self, tree, filename):
            self.tree = tree

        @classmethod
        def add_options(cls, parser):
            parser.add_option('--max-complexity', default=-1, action='store',
                              type='int', help="McCabe complexity threshold")
            parser.config_options.append('max-complexity')

        @classmethod
        def parse_options(cls, options):
            cls.max_complexity = options.max_complexity

        def run(self):
            if self.max_complexity < 0:
                return
            visitor = PathGraphingAstVisitor()
            visitor.preorder(self.tree, visitor)
            for graph in visitor.graphs.values():
                if graph.complexity() >= self.max_complexity:
                    text = self._error_tmpl % (graph.entity, graph.complexity())
                    yield graph.lineno, 0, text, type(self)

Since that is the defined entry point in the above ``setup.py``, flake8 finds
it and uses it to register the extension.

Existing Extensions
===================

This is not at all a comprehensive listing of existing extensions but simply a 
listing of the ones we are aware of:

* `flake8-immediate <https://github.com/schlamar/flake8-immediate>`_
  
* `flake8-todo <https://github.com/schlamar/flake8-todo>`_

* `pep8-naming <https://github.com/flintwork/pep8-naming>`_

.. links
.. _mccabe: https://github.com/flintwork/mccabe
.. _PyPI: https://pypi.python.org/pypi/
