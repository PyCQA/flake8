Plugin Handling
===============

Plugin Management
-----------------

Flake8 3.0 added support for two other plugins besides those which define new
checks. It now supports:

- extra checks

- alternative report formatters

- listeners to auto-correct violations of checks

To facilitate this, Flake8 needed a more mature way of managing plugins. As
such, we developed the |PluginManager| which accepts a namespace and will load
the plugins for that namespace. A |PluginManager| creates and manages many
|Plugin| instances.

A |Plugin| lazily loads the underlying entry-point provided by setuptools.
The entry-point will be loaded either by calling
:meth:`~flake8.plugins.manager.Plugin.load_plugin` or accessing the ``plugin``
attribute. We also use this abstraction to retrieve options that the plugin
wishes to register and parse.

The only public method that the |PluginManager| provides is
:meth:`~flake8.plugins.manager.PluginManager.map`. This will accept a function
(or other callable) and call it with each plugin as the first parameter.

We build atop the |PluginManager| with the |PTM|. It is expected that users of
the |PTM| will subclass it and specify the ``namespace``, e.g.,

.. code-block:: python

    class ExamplePluginType(flake8.plugin.manager.PluginTypeManager):
        namespace = 'example-plugins'

This provides a few extra methods via the |PluginManager|'s ``map`` method.

Finally, we create three classes of plugins:

- :class:`~flake8.plugins.manager.Checkers`

- :class:`~flake8.plugins.manager.Listeners`

- :class:`~flake8.plugins.manager.ReportFormatters`

These are used to interact with each of the types of plugins individually.

.. note::

    Our inspiration for our plugin handling comes from the author's extensive
    experience with ``stevedore``.

API Documentation
-----------------

.. autoclass:: flake8.plugins.manager.PluginManager
    :members:
    :special-members: __init__, __contains__, __getitem__

.. autoclass:: flake8.plugins.manager.Plugin
    :members:
    :special-members: __init__

.. autoclass:: flake8.plugins.manager.PluginTypeManager
    :members:

.. autoclass:: flake8.plugins.manager.Checkers

.. autoclass:: flake8.plugins.manager.Listeners

.. autoclass:: flake8.plugins.manager.ReportFormatters

.. |PluginManager| replace:: :class:`~flake8.plugins.manager.PluginManager`
.. |Plugin| replace:: :class:`~flake8.plugins.manager.Plugin`
.. |PTM| replace:: :class:`~flake8.plugins.manager.PluginTypeManager`
