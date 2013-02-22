======
Flake8
======

Flake8 is a wrapper around these tools:

- PyFlakes
- pep8
- Ned's McCabe script

Flake8 runs all the tools by launching the single 'flake8' script.
It displays the warnings in a per-file, merged output.

It also adds a few features:

- files that contain this line are skipped::

    # flake8: noqa

- lines that contain a "# noqa" comment at the end will not issue warnings.
- a Git and a Mercurial hook.
- a McCabe complexity checker.
- extendable through ``flake8.extension`` entry points.


QuickStart
==========

To run flake8 just invoke it against any directory or Python module::

    $ flake8 coolproject
    coolproject/mod.py:97:1: F401 'shutil' imported but unused
    coolproject/mod.py:625:17: E225 missing whitespace around operato
    coolproject/mod.py:729: F811 redefinition of function 'readlines' from line 723
    coolproject/mod.py:1028: F841 local variable 'errors' is assigned to but never used

The outputs of PyFlakes *and* pep8 (and the optional plugins) are merged
and returned.

flake8 offers an extra option: --max-complexity, which will emit a warning if
the McCabe complexity of a function is higher than the value.  By default it's
deactivated::

    $ flake8 --max-complexity 12 coolproject
    coolproject/mod.py:97:1: F401 'shutil' imported but unused
    coolproject/mod.py:625:17: E225 missing whitespace around operator
    coolproject/mod.py:729:1: F811 redefinition of unused 'readlines' from line 723
    coolproject/mod.py:939:1: C901 'Checker.check_all' is too complex (12)
    coolproject/mod.py:1028:1: F841 local variable 'errors' is assigned to but never used
    coolproject/mod.py:1204:1: C901 'selftest' is too complex (14)

This feature is quite useful to detect over-complex code.  According to McCabe,
anything that goes beyond 10 is too complex.
See https://en.wikipedia.org/wiki/Cyclomatic_complexity.


Configuration
-------------

The behaviour may be configured at two levels.

The user settings are read from the ``~/.config/flake8`` file.
Example::

  [flake8]
  ignore = E226,E302,E41
  max-line-length = 160

At the project level, a ``tox.ini`` file or a ``setup.cfg`` file is read
if present.  Only the first file is considered.  If this file does not
have a ``[flake8]`` section, no project specific configuration is loaded.

If the ``ignore`` option is not in the configuration and not in the arguments,
only the error codes ``E226`` and ``E241/E242`` are ignored
(see codes in the table below).


Mercurial hook
==============

To use the Mercurial hook on any *commit* or *qrefresh*, change your .hg/hgrc
file like this::

    [hooks]
    commit = python:flake8.run.hg_hook
    qrefresh = python:flake8.run.hg_hook

    [flake8]
    strict = 0
    complexity = 12


If *strict* option is set to **1**, any warning will block the commit. When
*strict* is set to **0**, warnings are just printed to the standard output.

*complexity* defines the maximum McCabe complexity allowed before a warning
is emitted.  If you don't specify it, it's just ignored.  If specified, it must
be a positive value.  12 is usually a good value.


Git hook
========

To use the Git hook on any *commit*, add a **pre-commit** file in the
*.git/hooks* directory containing::

    #!/usr/bin/python
    import sys
    from flake8.run import git_hook

    COMPLEXITY = 10
    STRICT = False

    if __name__ == '__main__':
        sys.exit(git_hook(complexity=COMPLEXITY, strict=STRICT, ignore='E501'))


If *strict* option is set to **True**, any warning will block the commit. When
*strict* is set to **False** or omitted, warnings are just printed to the
standard output.

*complexity* defines the maximum McCabe complexity allowed before a warning
is emitted.  If you don't specify it or set it to **-1**, it's just ignored.
If specified, it must be a positive value.  12 is usually a good value.

*lazy* when set to ``True`` will also take into account files not added to the
index.

Also, make sure the file is executable and adapt the shebang line so it
points to your Python interpreter.


Buildout integration
=====================

In order to use Flake8 inside a buildout, edit your buildout.cfg and add this::

    [buildout]

    parts +=
        ...
        flake8

    [flake8]
    recipe = zc.recipe.egg
    eggs = flake8
           ${buildout:eggs}
    entry-points =
        flake8=flake8.main:main


setuptools integration
======================

If setuptools is available, Flake8 provides a command that checks the
Python files declared by your project.  To use it, add flake8 to your
setup_requires::

    setup(
        name="project",
        packages=["project"],

        setup_requires=[
            "flake8"
        ]
    )

Running ``python setup.py flake8`` on the command line will check the
files listed in your ``py_modules`` and ``packages``.  If any warning
is found, the command will exit with an error code::

    $ python setup.py flake8



Original projects
=================

Flake8 is just a glue project, all the merits go to the creators of the original
projects:

- pep8: https://github.com/jcrocholl/pep8
- PyFlakes: https://launchpad.net/pyflakes
- McCabe: http://nedbatchelder.com/blog/200803/python_code_complexity_microtool.html


Warning / Error codes
=====================

The convention of Flake8 is to assign a code to each error or warning, like
the ``pep8`` tool.  These codes are used to configure the list of errors
which are selected or ignored.

Each code consists of an upper case ASCII letter followed by three digits.
The recommendation is to use a different prefix for each plugin.

A list of the known prefixes is published below:

- ``E***``/``W***``: `pep8 errors and warnings
  <http://pep8.readthedocs.org/en/latest/intro.html#error-codes>`_
- ``F***``: PyFlakes codes (see below)
- ``C9**``: McCabe complexity plugin `mccabe
  <https://github.com/flintwork/mccabe>`_
- ``N8**``: Naming Conventions plugin `pep8-naming
  <https://github.com/flintwork/pep8-naming>`_ (planned)


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


Links
-----

* `pep8 documentation <http://pep8.readthedocs.org/>`_

* `flake8 documentation <https://bitbucket.org/tarek/flake8/src/tip/README.rst>`_
