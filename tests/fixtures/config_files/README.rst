About this directory
====================

The files in this directory are test fixtures for unit and integration tests.
Their purpose is described below. Please note the list of file names that can
not be created as they are already used by tests.

New fixtures are preferred over updating existing features unless existing
tests will fail.

Files that should not be created
--------------------------------

- ``tests/fixtures/config_files/missing.ini``

Purposes of existing fixtures
-----------------------------

``tests/fixtures/config_files/cli-specified.ini``

    This should only be used when providing config file(s) specified by the
    user on the command-line.

``tests/fixtures/config_files/local-config.ini``

    This should be used when providing config files that would have been found
    by looking for config files in the current working project directory.

``tests/fixtures/config_files/local-plugin.ini``

    This is for testing configuring a plugin via flake8 config file instead of
    setuptools entry-point.

``tests/fixtures/config_files/no-flake8-section.ini``

    This should be used when parsing an ini file without a ``[flake8]``
    section.

``tests/fixtures/config_files/user-config.ini``

    This is an example configuration file that would be found in the user's
    home directory (or XDG Configuration Directory).
