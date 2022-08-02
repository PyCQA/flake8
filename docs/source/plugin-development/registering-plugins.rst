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
        url="https://github.com/me/flake8_example",
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

|Flake8| presently looks at two groups:

- ``flake8.extension``

- ``flake8.report``

If your plugin is one that adds checks to |Flake8|, you will use
``flake8.extension``. If your plugin performs extra report
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

    X101 = flake8_example:ExamplePlugin

In the above case, the entry-point name and the error code produced by your
plugin are the same.

If your plugin reports several error codes that all start with ``X10``, then
it would look like::

    X10 = flake8_example:ExamplePlugin

In this casae as well as the following case, your entry-point name acts as
a prefix to the error codes produced by your plugin.

If all of your plugin's error codes start with ``X1`` then it would look
like::

    X1 = flake8_example:ExamplePlugin

Finally, if all of your plugin's error codes start with just ``X`` then it
would look like the original example.

|Flake8| requires each entry point to be unique amongst all plugins installed
in the users environment. Selecting an entry point that is already used can
cause plugins to be deactivated without warning!

**Please Note:** Your entry point does not need to be exactly 4 characters
as of |Flake8| 3.0. Single letter entry point prefixes (such as the
'X' in the examples above) have caused issues in the past.  As such,
please consider using a 2 or 3 character entry point prefix,
i.e., ``ABC`` is better than ``A`` but ``ABCD`` is invalid.
*A 3 letters entry point prefix followed by 3 numbers (i.e.* ``ABC123`` *)
is currently the longest allowed entry point name.*


.. _Entry Points:
    https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points
