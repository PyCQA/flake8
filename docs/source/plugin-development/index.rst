============================
 Writing Plugins for Flake8
============================

Since |Flake8| 2.0, the |Flake8| tool has allowed for extensions and custom
plugins. In |Flake8| 3.0, we're expanding that ability to customize and
extend **and** we're attempting to thoroughly document it. Some of the
documentation in this section may reference third-party documentation to
reduce duplication and to point you, the developer, towards the authoritative
documentation for those pieces.

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


Video Tutorial
==============

Here's a tutorial which goes over building an ast checking plugin from scratch:

.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto; margin-bottom: 1em;">
        <iframe src="https://www.youtube.com/embed/ot5Z4KQPBL8" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>


.. toctree::
    :caption: Plugin Developer Documentation
    :maxdepth: 2

    registering-plugins
    plugin-parameters
    formatters


.. _entry points:
    https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points
