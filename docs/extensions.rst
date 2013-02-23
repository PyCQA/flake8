Writing an Extension for Flake8
===============================

If you plan on supporting python 2.5 you need to first do ``from __future__ 
import with_statement``. Every version of python greater than 2.5 already has 
the with statement built-in. After that, you should only ever need to import 
``setup`` from ``setuptools``. We're using entry points for extension 
management and this is the most sane way of doing things. This also means that 
you should specify that the installation requires (at least) ``setuptools``.  
Finally you'll need to specify your entry points, e.g., ::

    setup(
        entry_points={
            'flake8.extension': ['P10 = package.PackageEntryClass'],
        }
    )

Below is an example from mccabe_ for how to write your ``setup.py`` file for 
your Flake8 extension.

.. code-block:: python

    # https://github.com/florentx/mccabe/blob/master/setup.py
    # -*- coding: utf-8 -*-
    from __future__ import with_statement
    from setuptools import setup


    def get_version(fname='mccabe.py'):
        with open(fname) as f:
            for line in f:
                if line.startswith('__version__'):
                    return eval(line.split('=')[-1])


    def get_long_description():
        descr = []
        for fname in ('README.rst',):
            with open(fname) as f:
                descr.append(f.read())
        return '\n\n'.join(descr)


    setup(
        name='mccabe',
        version=get_version(),
        description="McCabe checker, plugin for flake8",
        long_description=get_long_description(),
        keywords='flake8 mccabe',
        author='Tarek Ziade',
        author_email='tarek@ziade.org',
        maintainer='Florent Xicluna',
        maintainer_email='florent.xicluna@gmail.com',
        url='https://github.com/florentx/mccabe',
        license='Expat license',
        py_modules=['mccabe'],
        zip_safe=False,
        install_requires=[
            'setuptools',
        ],
        entry_points={
            'flake8.extension': [
                'C90 = mccabe:McCabeChecker',
            ],
        },
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Quality Assurance',
        ],
    )

In ``mccabe.py`` you can see that extra options are added to the parser when 
flake8 registers the extensions:

.. code-block:: python

    # https://github.com/florentx/mccabe/blob/e88be51e0c6c2bd1b87d7a44b7e71b78fdc53959/mccabe.py#L225
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

.. links
.. _mccabe: https://github.com/florentx/mccabe
.. _PyPI: https://pypi.python.org/pypi/
