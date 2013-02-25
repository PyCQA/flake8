VCS Hooks
=========

Mercurial hook
--------------

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
--------

To use the Git hook on any *commit*, add a **pre-commit** file in the
*.git/hooks* directory containing::

    #!/usr/bin/env python
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
