=============================
 Using Version Control Hooks
=============================

Usage with the `pre-commit`_ git hooks framework
================================================

|Flake8| can be included as a hook for `pre-commit`_.  The easiest way to get
started is to add this configuration to your ``.pre-commit-config.yaml``:

.. code-block:: yaml

    -   repo: https://github.com/pycqa/flake8
        rev: ''  # pick a git hash / tag to point to
        hooks:
        -   id: flake8

See the `pre-commit docs`_ for how to customize this configuration.

Checked-in python files will be passed as positional arguments.  ``flake8``
will always lint explicitly passed arguments (:option:`flake8 --exclude` has
no effect).  Instead use ``pre-commit``'s ``exclude: ...`` regex to exclude
files.  ``pre-commit`` won't ever pass untracked files to ``flake8`` so
excluding ``.git`` / ``.tox`` / etc. is unnecessary.

.. code-block:: yaml

        -   id: flake8
            exclude: ^testing/(data|examples)/

``pre-commit`` creates an isolated environment for hooks.  To use ``flake8``
plugins, use the ``additional_dependencies`` setting.

.. code-block:: yaml

        -   id: flake8
            additional_dependencies: [flake8-docstrings]

.. _pre-commit:
    https://pre-commit.com/
.. _pre-commit docs:
    https://pre-commit.com/#pre-commit-configyaml---hooks
