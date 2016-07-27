.. _register-a-plugin:

==================================
 Registering a Plugin with Flake8
==================================

To register any kind of plugin with |Flake8|, you need:

#. A way to install the plugin (whether it is packaged on its own or
   as part of something else). In this section, we will use a ``setup.py``
   written for an example plugin.

#. A name for your plugin that will (ideally) be unique.

#. A somewhat recent version of setuptools (newer than 0.7.0 but preferably as
   recent as you can attain).

|Flake8| relies on functionality provided by setuptools called
`Entry Points`_. These allow any package to register a plugin with |Flake8|
via that package's ``setup.py`` file.

Let's presume that we already have our plugin written and it's in a module
called ``flake8_example``. We might have a ``setup.py`` that looks something
like:

.. code-block:: python

    from __future__ import with_statement
    import setuptools

    requires = [
        "flake8 > 3.0.0",
    ]

    flake8_entry_point = # ...

    setuptools.setup(
        name="flake8_example",
        license="MIT",
        version="0.1.0",
        description="our extension to flake8",
        author="Me",
        author_email="example@example.com",
        url="https://gitlab.com/me/flake8_example",
        packages=[
            "flake8_example",
        ],
        install_requires=requires,
        entry_points={
            flake8_entry_point: [
                'X = flake8_example:ExamplePlugin',
            ],
        },
        classifiers=[
            "Framework :: Flake8",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Quality Assurance",
        ],
    )

Note specifically these lines:

.. code-block:: python

    flake8_entry_point = # ...

    setuptools.setup(
        # snip ...
        entry_points={
            flake8_entry_point: [
                'X = flake8_example:ExamplePlugin',
            ],
        },
        # snip ...
    )

We tell setuptools to register our entry point ``X`` inside the specific
grouping of entry-points that flake8 should look in.

|Flake8| presently looks at three groups:

- ``flake8.extension``

- ``flake8.listen``

- ``flake8.report``

If your plugin is one that adds checks to |Flake8|, you will use
``flake8.extension``. If your plugin automatically fixes errors in code, you
will use ``flake8.listen``.  Finally, if your plugin performs extra report
handling (formatting, filtering, etc.) it will use ``flake8.report``.

If our ``ExamplePlugin`` is something that adds checks, our code would look
like:

.. code-block:: python

    setuptools.setup(
        # snip ...
        entry_points={
            'flake8.extension': [
                'X = flake8_example:ExamplePlugin',
            ],
        },
        # snip ...
    )

The ``X`` in checking plugins define what error codes it is going to report.
So if the plugin reports only the error code ``X101`` your entry-point would
look like::

    X101 = flake8_example.ExamplePlugin

If your plugin reports several error codes that all start with ``X10``, then
it would look like::

    X10 = flake8_example.ExamplePlugin

If all of your plugin's error codes start with ``X1`` then it would look
like::

    X1 = flake8_example.ExamplePlugin

Finally, if all of your plugin's error codes start with just ``X`` then it
would look like the original example.


.. _Entry Points:
    https://pythonhosted.org/setuptools/pkg_resources.html#entry-points
