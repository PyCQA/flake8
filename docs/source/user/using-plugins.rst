==================================
 Using Plugins For Fun and Profit
==================================

|Flake8| is useful on its own but a lot of |Flake8|'s popularity is due to
its extensibility. Our community has developed :term:`plugin`\ s that augment
|Flake8|'s behaviour. Most of these plugins are uploaded to PyPI_. The
developers of these plugins often have some style they wish to enforce.

For example, `flake8-docstrings`_ adds a check for :pep:`257` style
conformance. Others attempt to enforce consistency, like `flake8-quotes`_.

.. note::

    The accuracy or reliability of these plugins may vary wildly from plugin
    to plugin and not all plugins are guaranteed to work with |Flake8| 3.0.

To install a third-party plugin, make sure that you know which version of
Python (or pip) you used to install |Flake8|. You can then use the most
appropriate of:

.. prompt:: bash

    pip install <plugin-name>
    pip3 install <plugin-name>
    python -m pip install <plugin-name>
    python3 -m pip install <plugin-name>
    python3.9 -m pip install <plugin-name>

To install the plugin, where ``<plugin-name>`` is the package name on PyPI_.
To verify installation use:

.. prompt:: bash

    flake8 --version
    python<version> -m flake8 --version

To see the plugin's name and version in the output.

.. seealso:: :ref:`How to Invoke Flake8 <invocation>`

After installation, most plugins immediately start reporting :term:`error`\ s.
Check the plugin's documentation for which error codes it returns and if it
disables any by default.

.. note::

    You can use both :option:`flake8 --select` and :option:`flake8 --ignore`
    with plugins.

Some plugins register new options, so be sure to check :option:`flake8 --help`
for new flags and documentation. These plugins may also allow these flags to
be specified in your configuration file. Hopefully, the plugin authors have
documented this for you.

.. seealso:: :ref:`Configuring Flake8 <configuration>`


.. _PyPI:
    https://pypi.org/
.. _flake8-docstrings:
    https://pypi.org/project/flake8-docstrings/
.. _flake8-quotes:
    https://pypi.org/project/flake8-quotes/
