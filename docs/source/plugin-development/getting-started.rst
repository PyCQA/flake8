.. _getting-started:

===============
Getting Started
===============

To get started writing a |Flake8| :term:`plugin` you first need:

- An idea for a plugin

- An available package name on PyPI

- One or more versions of Python installed

- A text editor or IDE of some kind

- An idea of what *kind* of plugin you want to build:

  * Formatter

  * Check

Once you've gathered these things, you can get started.

All plugins for |Flake8| must be registered via `entry points`_. In this
section we cover:

- How to register your plugin so |Flake8| can find it

- How to make |Flake8| provide your check plugin with information (via
  command-line flags, function/class parameters, etc.)

- How to make a formatter plugin

- How to write your check plugin so that it works with |Flake8| 2.x and 3.x


.. _entry points:
    https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points
