Configuration
=============

The behaviour may be configured at two levels.

Global
------

The user settings are read from the ``~/.config/flake8`` file.
Example::

  [flake8]
  ignore = E226,E302,E41
  max-line-length = 160
  exclude = tests/*
  max-complexity = 10

Per-Project
-----------

At the project level, a ``tox.ini`` file or a ``setup.cfg`` file is read
if present.  Only the first file is considered.  If this file does not
have a ``[flake8]`` section, no project specific configuration is loaded.

Default
-------

If the ``ignore`` option is not in the configuration and not in the arguments,
only the error codes ``E226`` and ``E241/E242`` are ignored
(see the :ref:`warning and error codes <error-codes>`).

Settings
--------

This is a (likely incomplete) list of settings that can be used in your config
file. In general, any settings that pep8 supports we also support and we add
the ability to set ``max-complexity`` as well.

- ``exclude``: comma-separated filename and glob patterns
  default: ``.svn,CVS,.bzr,.hg,.git,__pycache``

- ``filename``: comma-separated filename and glob patterns
  default: ``*.py``

- ``select``: select errors and warnings to enable which are off by default

- ``ignore``: skip errors or warnings

- ``max-line-length``: set maximum allowed line length
  default: 79

- ``format``: set the error format

- ``max-complexity``: McCabe complexity threshold
