======
Flake8
======

Flake8 is a wrapper around these tools:

- PyFlakes
- pep8
- Ned Batchelder's McCabe script

Flake8 runs all the tools by launching the single ``flake8`` script.
It displays the warnings in a per-file, merged output.

It also adds a few features:

- files that contain this line are skipped::

    # flake8: noqa

- lines that contain a ``# noqa`` comment at the end will not issue warnings.
- a Git and a Mercurial hook.
- a McCabe complexity checker.
- extendable through ``flake8.extension`` entry points.


QuickStart
==========

::

    pip install flake8

To run flake8 just invoke it against any directory or Python module::

    $ flake8 coolproject
    coolproject/mod.py:97:1: F401 'shutil' imported but unused
    coolproject/mod.py:625:17: E225 missing whitespace around operato
    coolproject/mod.py:729:1: F811 redefinition of function 'readlines' from line 723
    coolproject/mod.py:1028:1: F841 local variable 'errors' is assigned to but never used

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

Questions or Feedback
=====================

If you have questions you'd like to ask the developers, or feedback you'd like
to provide, feel free to use the mailing list: code-quality@python.org We
would love to hear from you. Additionally, if you have a feature you'd like to
suggest, the mailing list would be the best place for it.

.. _links:

Links
=====

* `flake8 documentation <http://flake8.readthedocs.org/en/latest/>`_

* `pep8 documentation <http://pep8.readthedocs.org/en/latest/>`_
