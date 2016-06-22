.. _glossary:

================================================
 Glossary of Terms Used in Flake8 Documentation
================================================

.. glossary::
    :sorted:

    formatter
        A :term:`plugin` that augments the output of |Flake8| when passed
        to :option:`flake8 --format`.

    plugin
        A package that is typically installed from PyPI to augment the
        behaviour of |Flake8| either through adding one or more additional
        :term:`check`\ s or providing additional :term:`formatter`\ s.

    check
        A piece of logic that corresponds to an error code. A check may
        be a style check (e.g., check the length of a given line against
        the user configured maximum) or a lint check (e.g., checking for
        unused imports) or some other check as defined by a plugin.

    error code
        The symbol associated with a specific :term:`check`. For example,
        pycodestyle implements :term:`check`\ s that look for whitespace
        around binary operators and will either return an error code of
        W503 or W504.
