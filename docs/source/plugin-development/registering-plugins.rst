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

|Flake8| requires each entry point to be unique amongst all plugins installed
in the users environment. Before defining your set of error codes, please
check the list below and select a unique entry point for your plugin.

+--------+-------------+---------------------------------+
| Letter | Entry Point |             Project             |
+--------+-------------+---------------------------------+
|    A   |     A00x    |         flake8-builtins         |
+--------+-------------+---------------------------------+
|        |     A40x    |          flake8-author          |
+--------+-------------+---------------------------------+
|    B   |     Bxxx    |          flake8-bugbear         |
+--------+-------------+---------------------------------+
|    C   |     C001    |        flake8-confusables       |
+--------+-------------+---------------------------------+
|        |     C10x    |          flake8-coding          |
+--------+-------------+---------------------------------+
|        |     C81x    |          flake8-commas          |
+--------+-------------+---------------------------------+
|        |     C90x    |              mccabe             |
+--------+-------------+---------------------------------+
|        |    CNL100   |       flake8-class-newline      |
+--------+-------------+---------------------------------+
|    D   |     Dxxx    |  flake8-docstring (pydocstyle)  |
+--------+-------------+---------------------------------+
|        |     D001    |        flake8-deprecated        |
+--------+-------------+---------------------------------+
|    E   |     Exxx    |           pycodestyle           |
+--------+-------------+---------------------------------+
|    F   |     Fxxx    |             pyflakes            |
+--------+-------------+---------------------------------+
|        |  FI10-FI90  |       flake8-future-import      |
+--------+-------------+---------------------------------+
|    I   |     Ixxx    |       flake8-import-order       |
+--------+-------------+---------------------------------+
|        |     I00x    |           flake8-isort          |
+--------+-------------+---------------------------------+
|        |     I20x    |       flake8-tidy-imports       |
+--------+-------------+---------------------------------+
|        |    IESxxx   | flake8-invalid-escape-sequences |
+--------+-------------+---------------------------------+
|    M   |     M001    |           flake8-mock           |
+--------+-------------+---------------------------------+
|        |     M90x    |         mutable-defaults        |
+--------+-------------+---------------------------------+
|        |     M90x    |          flake8-mutable         |
+--------+-------------+---------------------------------+
|    N   |     N8xx    |          flake8-naming          |
+--------+-------------+---------------------------------+
|        |     N999    |        flake8-module-name       |
+--------+-------------+---------------------------------+
|    O   |  O100-O102  |         flake8-ownership        |
+--------+-------------+---------------------------------+
|    P   |     Pxxx    |       flake8-string-format      |
+--------+-------------+---------------------------------+
|    Q   |     Q0xx    |          flake8-quotes          |
+--------+-------------+---------------------------------+
|        |     Q1xx    |          flake8-quotes2         |
+--------+-------------+---------------------------------+
|        |     Q4xx    |            flake8-sql           |
+--------+-------------+---------------------------------+
|    R   |     Rxxx    |           flake8-regex          |
+--------+-------------+---------------------------------+
|        |     R70x    |              radon              |
+--------+-------------+---------------------------------+
|        |    RSTxxx   |      flake8-rst-docstrings      |
+--------+-------------+---------------------------------+
|    S   |     Sxxx    |          flake8-strict          |
+--------+-------------+---------------------------------+
|        |     Sxxx    |         flake8-snippets         |
+--------+-------------+---------------------------------+
|        |     Sxxx    |          flake8-bandit          |
+--------+-------------+---------------------------------+
|        |     S00x    |        flake8-sorted-keys       |
+--------+-------------+---------------------------------+
|        |     S001    |         flake8-prep3101         |
+--------+-------------+---------------------------------+
|    T   |     Txxx    |          flake8-pytest          |
+--------+-------------+---------------------------------+
|        |     T000    |           flake8-todo           |
+--------+-------------+---------------------------------+
|        |     T00x    |           flake8-print          |
+--------+-------------+---------------------------------+
|        |     T004    |        flake8-libfaketime       |
+--------+-------------+---------------------------------+
|        |     T005    |       flake8-module-import      |
+--------+-------------+---------------------------------+
|        |     T006    |      flake8-ugettext-alias      |
+--------+-------------+---------------------------------+
|        |     T006    |   flake8-translation-activate   |
+--------+-------------+---------------------------------+
|        |     T007    |        flake8-user-model        |
+--------+-------------+---------------------------------+
|        |     T100    |         flake8-debugger         |
+--------+-------------+---------------------------------+
|        |     T4xx    |           flake8-mypy           |
+--------+-------------+---------------------------------+
|        |     T80x    |           flake8-tuple          |
+--------+-------------+---------------------------------+
|    W   |     Wxxx    |           pycodestyle           |
+--------+-------------+---------------------------------+


.. _Entry Points:
    https://pythonhosted.org/setuptools/pkg_resources.html#entry-points
