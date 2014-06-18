VCS Hooks
=========

flake8 can install hooks for Mercurial and Git so that flake8 is run
automatically before commits. The commit will fail if there are any
flake8 issues.

You can install the hook by issuing this command in the root of your
project::

  $ flake8 --install-hooks

In the case of Git, the hook won't be installed if a custom
``pre-commit`` hook file is already present in
the ``.git/hooks`` directory.

You can control the behavior of the pre-commit hook using environment
variables:

``FLAKE8_COMPLEXITY``
  Any value > 0 enables complexity checking with McCabe. (defaults
  to 10)

``FLAKE8_STRICT``
  If True, this causes the commit to fail in case of any errors at
  all. (defaults to False)

``FLAKE8_IGNORE``
  Comma-separated list of errors and warnings to ignore.  (defaults to
  empty)

``FLAKE8_LAZY``
  If True, also scans those files not added to the index before
  commit. (defaults to False)
