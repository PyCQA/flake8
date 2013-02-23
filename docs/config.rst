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

Per-Project
-----------

At the project level, a ``tox.ini`` file or a ``setup.cfg`` file is read
if present.  Only the first file is considered.  If this file does not
have a ``[flake8]`` section, no project specific configuration is loaded.

Default
-------

If the ``ignore`` option is not in the configuration and not in the arguments,
only the error codes ``E226`` and ``E241/E242`` are ignored
(see codes in the table below).
