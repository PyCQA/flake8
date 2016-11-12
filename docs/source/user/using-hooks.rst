=============================
 Using Version Control Hooks
=============================

|Flake8| can be integrated into your development workflow in many ways. A
default installation of |Flake8| can install pre-commit hooks for both
`Git`_ and `Mercurial`_. To install a built-in hook, you can use the
:option:`flake8 --install-hook` command-line option. For example, you can
install a git pre-commit hook by running:

.. prompt:: bash

    flake8 --install-hook git

This will install the pre-commit hook into ``.git/hooks/``. Alternatively,
you can install the mercurial commit hook by running

.. prompt:: bash

    flake8 --install-hook mercurial


Preventing Commits
==================

By default, |Flake8| does not prevent you from creating a commit with these
hooks. Both hooks can be configured to be strict easily.

Both our Git and Mercurial hooks check for the presence of ``flake8.strict``
in each VCS' config. For example, you might configure this like so:

.. prompt:: bash

    git config --bool flake8.strict true
    hg config flake8.strict true


Checking All Modified Files Currently Tracked
=============================================

.. note::

    Mercurial does not have the concept of an index or "stage" as best as I
    understand.

|Flake8| aims to make smart choices that keep things fast for users where
possible. As a result, the |Flake8| Git pre-commit will default to only
checking files that have been staged (i.e., added to the index). If, however,
you are keen to be lazy and not independenty add files to your git index, you
can set ``flake8.lazy`` to ``true`` (similar to how you would set
``flake8.strict`` above) and this will check all tracked files.

This is to support users who often find themselves doing things like:

.. prompt:: bash

    git commit -a

.. note::

    If you have files you have not yet added to the index, |Flake8| will not
    see these and will not check them for you. You must ``git-add`` them
    first.


.. _Git:
    https://git-scm.com/
.. _Mercurial:
    https://www.mercurial-scm.org/
