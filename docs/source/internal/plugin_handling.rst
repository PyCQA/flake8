Plugin Handling
===============

Plugin Management
-----------------

|Flake8| 3.0 added support for other plugins besides those which define
new checks. It now supports:

- extra checks

- alternative report formatters

To facilitate this, |Flake8| needed a more mature way of managing plugins.
Thus, we developed the |PluginManager| which accepts a namespace and will load
the plugins for that namespace. A |PluginManager| creates and manages many
|Plugin| instances.

A |Plugin| lazily loads the underlying entry-point provided by setuptools.
The entry-point will be loaded either by calling
:meth:`~flake8.plugins.manager.Plugin.load_plugin` or accessing the ``plugin``
attribute. We also use this abstraction to retrieve options that the plugin
wishes to register and parse.

The only public method the |PluginManager| provides is
:meth:`~flake8.plugins.manager.PluginManager.map`. This will accept a function
(or other callable) and call it with each plugin as the first parameter.

We build atop the |PluginManager| with the |PTM|. It is expected that users of
the |PTM| will subclass it and specify the ``namespace``, e.g.,

.. code-block:: python

    class ExamplePluginType(flake8.plugin.manager.PluginTypeManager):
        namespace = 'example-plugins'

This provides a few extra methods via the |PluginManager|'s ``map`` method.

Finally, we create two classes of plugins:

- :class:`~flake8.plugins.manager.Checkers`

- :class:`~flake8.plugins.manager.ReportFormatters`

These are used to interact with each of the types of plugins individually.

.. note::

    Our inspiration for our plugin handling comes from the author's extensive
    experience with ``stevedore``.

Default Plugins
---------------

Finally, |Flake8| has always provided its own plugin shim for Pyflakes. As
part of that we carry our own shim in-tree and now store that in
:mod:`flake8.plugins.pyflakes`.

|Flake8| also registers plugins for pep8. Each check in pep8 requires
different parameters and it cannot easily be shimmed together like Pyflakes
was. As such, plugins have a concept of a "group". If you look at our
:file:`setup.py` you will see that we register pep8 checks roughly like so:

.. code::

    pep8.<check-name> = pep8:<check-name>

We do this to identify that ``<check-name>>`` is part of a group. This also
enables us to special-case how we handle reporting those checks. Instead of
reporting each check in the ``--version`` output, we report ``pep8`` and check
``pep8`` the module for a ``__version__`` attribute. We only report it once
to avoid confusing users.

API Documentation
-----------------

.. autoclass:: flake8.plugins.manager.PluginManager
    :members:
    :special-members: __init__

.. autoclass:: flake8.plugins.manager.Plugin
    :members:
    :special-members: __init__

.. autoclass:: flake8.plugins.manager.PluginTypeManager
    :members:

.. autoclass:: flake8.plugins.manager.Checkers
    :members:

.. autoclass:: flake8.plugins.manager.ReportFormatters

.. |PluginManager| replace:: :class:`~flake8.plugins.manager.PluginManager`
.. |Plugin| replace:: :class:`~flake8.plugins.manager.Plugin`
.. |PTM| replace:: :class:`~flake8.plugins.manager.PluginTypeManager`
