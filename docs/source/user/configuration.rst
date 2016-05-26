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
