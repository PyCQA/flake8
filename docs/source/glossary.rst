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

    error
    error code
    violation
        The symbol associated with a specific :term:`check`. For example,
        pycodestyle implements :term:`check`\ s that look for whitespace
        around binary operators and will either return an error code of
        ``W503`` or ``W504``.

    warning
        Typically the ``W`` class of :term:`error code`\ s from pycodestyle.

    class
    error class
        A larger grouping of related :term:`error code`\ s. For example,
        ``W503`` and ``W504`` are two codes related to whitespace. ``W50``
        would be the most specific class of codes relating to whitespace.
        ``W`` would be the warning class that subsumes all whitespace
        errors.

    pyflakes
        The project |Flake8| depends on to lint files (check for unused
        imports, variables, etc.). This uses the ``F`` :term:`class` of
        :term:`error code`\ s reported by |Flake8|.

    pycodestyle
        The project |Flake8| depends on to provide style enforcement.
        pycodestyle implements :term:`check`\ s for :pep:`8`. This uses the
        ``E`` and ``W`` :term:`class`\ es of :term:`error code`\ s.

    mccabe
        The project |Flake8| depends on to calculate the McCabe complexity
        of a unit of code (e.g., a function). This uses the ``C``
        :term:`class` of :term:`error code`\ s.
