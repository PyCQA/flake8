Configuration
=============

Configuration settings are applied in three ways: user, project, and the
``--config`` CLI argument. The user (global) configuration is read first. Next
the project configuration is loaded, and overrides any settings found in both
the user (global) and project configurations. Finally, if the ``--config``
argument is used on the command line, the specified file is loaded and
overrides any settings that overlap with the user (global) and project
configurations.


User (Global)
-------------

The user settings are read from the ``~/.config/flake8`` file (or the
``~/.flake8`` file on Windows).
Example::

  [flake8]
  ignore = E226,E302,E41
  max-line-length = 160
  exclude = tests/*
  max-complexity = 10

Per-Project
-----------

At the project level, the ``tox.ini``, ``setup.cfg``, ``.pep8`` or ``.flake8``
files are read if present.  Only the first file is considered.  If this file
does not have a ``[flake8]`` section, no project specific configuration is
loaded.

Per Code Line
-------

To ignore one line of code add ``# NOQA`` as a line comment.

Default
-------

If the ``ignore`` option is not in the configuration and not in the arguments,
the error codes ``E121/E123/E126``, ``E226``, ``E241/E242``, ``E704`` and
``W503`` are ignored (see :ref:`warning and error codes <error-codes>` for their
their meaning).

Settings
--------

This is a (likely incomplete) list of settings that can be used in your config
file. In general, any settings that ``pycodestyle`` supports we also support and
we add the ability to set ``max-complexity`` as well.

- ``exclude``: comma-separated filename and glob patterns
  default: ``.svn,CVS,.bzr,.hg,.git,__pycache__``

- ``filename``: comma-separated filename and glob patterns
  default: ``*.py``

- ``select``: select errors and warnings to enable which are off by default

- ``ignore``: skip errors or warnings

- ``max-line-length``: set maximum allowed line length
  default: 79

- ``format``: set the error format

- ``max-complexity``: McCabe complexity threshold
