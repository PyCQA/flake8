====================
 Configuring Flake8
====================

Once you have learned how to :ref:`invoke <invocation>` Flake8, you will soon
want to learn how to configure it so you do not have to specify the same
options every time you use it.

This section will show you how to make

.. prompt:: bash

    flake8

Remember that you want to specify certain options without writing

.. prompt:: bash

    flake8 --select E123,W456 --enable-extensions H111


Configuration Locations
=======================

Presently, Flake8 supports storing its configuration in the following places:

- Your top-level user directory

- In your project in one of ``setup.cfg``, ``tox.ini``, or ``.flake8``.


"User" Configuration
--------------------

Flake8 allows a user to use "global" configuration file to store preferences.
The user configuration file is expected to be stored somewhere in the user's
"home" directory.

- On Windows the "home" directory will be something like
  ``C:\\Users\sigmavirus24``, a.k.a, ``~\``.

- On Linux and other Unix like systems (including OS X) we will look in
  ``~/``.

Note that Flake8 looks for ``~\.flake8`` on Windows and ``~/.config/flake8``
on Linux and other Unix systems.


Project Configuration
---------------------

Flake8 is written with the understanding that people organize projects into
sub-directories. Let's take for example Flake8's own project structure

.. code::

    flake8
    ├── docs
    │   ├── build
    │   └── source
    │       ├── _static
    │       ├── _templates
    │       ├── dev
    │       ├── internal
    │       └── user
    ├── flake8
    │   ├── formatting
    │   ├── main
    │   ├── options
    │   └── plugins
    └── tests
        ├── fixtures
        │   └── config_files
        ├── integration
        └── unit

In the top-level ``flake8`` directory (which contains ``docs``, ``flake8``,
and ``tests``) there's also ``tox.ini`` and ``setup.cfg`` files.
