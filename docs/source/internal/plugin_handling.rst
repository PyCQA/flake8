Plugin Handling
===============

Plugin Management
-----------------

|Flake8| 3.0 added support for other plugins besides those which define
new checks. It now supports:

- extra checks

- alternative report formatters

Default Plugins
---------------

Finally, |Flake8| has always provided its own plugin shim for Pyflakes. As
part of that we carry our own shim in-tree and now store that in
:mod:`flake8.plugins.pyflakes`.

|Flake8| also registers plugins for pycodestyle. Each check in pycodestyle
requires different parameters and it cannot easily be shimmed together like
Pyflakes was. As such, plugins have a concept of a "group". If you look at our
:file:`setup.py` you will see that we register pycodestyle checks roughly like
so:

.. code::

    pycodestyle.<check-name> = pycodestyle:<check-name>

We do this to identify that ``<check-name>>`` is part of a group. This also
enables us to special-case how we handle reporting those checks. Instead of
reporting each check in the ``--version`` output, we only report
``pycodestyle`` once.

API Documentation
-----------------

.. autofunction:: flake8.plugins.finder.parse_plugin_options

.. autofunction:: flake8.plugins.finder.find_plugins

.. autofunction:: flake8.plugins.finder.load_plugins
