CHANGES
=======

2.4.0 - 2015-03-07
------------------

- **Bug** Print filenames when using multiprocessing and ``-q`` option.
  (`GitLab#31`_)

- **Bug** Put upper cap on dependencies. The caps for 2.4.0 are:

  - ``pep8 < 1.6`` (Related to `GitLab#35`_)

  - ``mccabe < 0.4``

  - ``pyflakes < 0.9``

  See also `GitLab#32`_

- **Bug** Files excluded in a config file were not being excluded when flake8
  was run from a git hook. (`GitHub#2`_)

- **Improvement** Print warnings for users who are providing mutually
  exclusive options to flake8. (`GitLab#8`_, `GitLab!18`_)

- **Feature** Allow git hook configuration to live in ``.git/config``.
  See the updated `VCS hooks docs`_ for more details. (`GitLab!20`_)

.. _GitHub#2: https://github.com/pycqa/flake8/pull/2
.. _GitLab#8: https://gitlab.com/pycqa/flake8/issues/8
.. _GitLab#31: https://gitlab.com/pycqa/flake8/issues/31
.. _GitLab#32: https://gitlab.com/pycqa/flake8/issues/32
.. _GitLab#35: https://gitlab.com/pycqa/flake8/issues/35
.. _GitLab!18: https://gitlab.com/pycqa/flake8/merge_requests/18
.. _GitLab!20: https://gitlab.com/pycqa/flake8/merge_requests/20
.. _VCS hooks docs: https://flake8.readthedocs.org/en/latest/vcs.html

2.3.0 - 2015-01-04
------------------

- **Feature**: Add ``--output-file`` option to specify a file to write to
  instead of ``stdout``.

- **Bug** Fix interleaving of output while using multiprocessing
  (`GitLab#17`_)

.. _GitLab#17: https://gitlab.com/pycqa/flake8/issues/17

2.2.5 - 2014-10-19
------------------

- Flush standard out when using multiprocessing

- Make the check for "# flake8: noqa" more strict

2.2.4 - 2014-10-09
------------------

- Fix bugs triggered by turning multiprocessing on by default (again)

  Multiprocessing is forcibly disabled in the following cases:

  - Passing something in via stdin

  - Analyzing a diff

  - Using windows

- Fix --install-hook when there are no config files present for pep8 or
  flake8.

- Fix how the setuptools command parses excludes in config files

- Fix how the git hook determines which files to analyze (Thanks Chris
  Buccella!)

2.2.3 - 2014-08-25
------------------

- Actually turn multiprocessing on by default

2.2.2 - 2014-07-04
------------------

- Re-enable multiprocessing by default while fixing the issue Windows users
  were seeing.

2.2.1 - 2014-06-30
------------------

- Turn off multiple jobs by default. To enable automatic use of all CPUs, use
  ``--jobs=auto``. Fixes #155 and #154.

2.2.0 - 2014-06-22
------------------

- New option ``doctests`` to run Pyflakes checks on doctests too
- New option ``jobs`` to launch multiple jobs in parallel
- Turn on using multiple jobs by default using the CPU count
- Add support for ``python -m flake8`` on Python 2.7 and Python 3
- Fix Git and Mercurial hooks: issues #88, #133, #148 and #149
- Fix crashes with Python 3.4 by upgrading dependencies
- Fix traceback when running tests with Python 2.6
- Fix the setuptools command ``python setup.py flake8`` to read
  the project configuration


2.1.0 - 2013-10-26
------------------

- Add FLAKE8_LAZY and FLAKE8_IGNORE environment variable support to git and
  mercurial hooks
- Force git and mercurial hooks to repsect configuration in setup.cfg
- Only check staged files if that is specified
- Fix hook file permissions
- Fix the git hook on python 3
- Ignore non-python files when running the git hook
- Ignore .tox directories by default
- Flake8 now reports the column number for PyFlakes messages


2.0.0 - 2013-02-23
------------------

- Pyflakes errors are prefixed by an ``F`` instead of an ``E``
- McCabe complexity warnings are prefixed by a ``C`` instead of a ``W``
- Flake8 supports extensions through entry points
- Due to the above support, we **require** setuptools
- We publish the `documentation <https://flake8.readthedocs.org/>`_
- Fixes #13: pep8, pyflakes and mccabe become external dependencies
- Split run.py into main.py, engine.py and hooks.py for better logic
- Expose our parser for our users
- New feature: Install git and hg hooks automagically
- By relying on pyflakes (0.6.1), we also fixed #45 and #35


1.7.0 - 2012-12-21
------------------

- Fixes part of #35: Exception for no WITHITEM being an attribute of Checker
  for Python 3.3
- Support stdin
- Incorporate @phd's builtins pull request
- Fix the git hook
- Update pep8.py to the latest version


1.6.2 - 2012-11-25
------------------

- fixed the NameError: global name 'message' is not defined (#46)


1.6.1 - 2012-11-24
------------------

- fixed the mercurial hook, a change from a previous patch was not properly
  applied
- fixed an assumption about warnings/error messages that caused an exception
  to be thrown when McCabe is used


1.6 - 2012-11-16
----------------

- changed the signatures of the ``check_file`` function in flake8/run.py,
  ``skip_warning`` in flake8/util.py and the ``check``, ``checkPath``
  functions in flake8/pyflakes.py.
- fix ``--exclude`` and ``--ignore`` command flags (#14, #19)
- fix the git hook that wasn't catching files not already added to the index
  (#29)
- pre-emptively includes the addition to pep8 to ignore certain lines.
  Add ``# nopep8`` to the end of a line to ignore it. (#37)
- ``check_file`` can now be used without any special prior setup (#21)
- unpacking exceptions will no longer cause an exception (#20)
- fixed crash on non-existent file (#38)


1.5 - 2012-10-13
----------------

- fixed the stdin
- make sure mccabe catches the syntax errors as warnings
- pep8 upgrade
- added max_line_length default value
- added Flake8Command and entry points if setuptools is around
- using the setuptools console wrapper when available


1.4 - 2012-07-12
----------------

- git_hook: Only check staged changes for compliance
- use pep8 1.2


1.3.1 - 2012-05-19
------------------

- fixed support for Python 2.5


1.3 - 2012-03-12
----------------

- fixed false W402 warning on exception blocks.


1.2 - 2012-02-12
----------------

- added a git hook
- now Python 3 compatible
- mccabe and pyflakes have warning codes like pep8 now


1.1 - 2012-02-14
----------------

- fixed the value returned by --version
- allow the flake8: header to be more generic
- fixed the "hg hook raises 'physical lines'" bug
- allow three argument form of raise
- now uses setuptools if available, for 'develop' command


1.0 - 2011-11-29
----------------

- Deactivates by default the complexity checker
- Introduces the complexity option in the HG hook and the command line.


0.9 - 2011-11-09
----------------

- update pep8 version to 0.6.1
- mccabe check: gracefully handle compile failure


0.8 - 2011-02-27
----------------

- fixed hg hook
- discard unexisting files on hook check


0.7 - 2010-02-18
----------------

- Fix pep8 initialization when run through Hg
- Make pep8 short options work when run through the command line
- Skip duplicates when controlling files via Hg


0.6 - 2010-02-15
----------------

- Fix the McCabe metric on some loops
