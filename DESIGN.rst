==============
 Design Goals
==============

Outline
-------

#. :ref:`plugins`

   #. :ref:`checking`

   #. :ref:`autofixing`

   #. :ref:`reporter-plugins`

   #. :ref:`options-passing`

   #. :ref:`plugin-default-ignore`

   #. :ref:`report-generation`

#. :ref:`options`

   #. :ref:`better-select-ignore`

#. :ref:`standard-in`

#. :ref:`multiprocessing`

.. _plugins:

Better Plugins Support
----------------------

Currently, Flake8 has some rather excellent support for plugins. It currently
allows for the following:

- Third-party packages to register checks

- Checks to be disabled by default

- Checks to accept an AST compiled tree, physical lines, or logical lines.

- Flake8 handles running those checks in separate subprocesses as necessary

That said, plugins cannot access the options passed on the command-line, or
options parsed from config files (without parsing them, themselves) and all
reporting is handled by pep8 instead of flake8 which reduces the flexibility
users have in aggregating reports.

.. _checking:

Support for Plugins that Only Run Checks
++++++++++++++++++++++++++++++++++++++++

Flake8 currently already supports plugins that only run checks. This support
needs to continue and should be trivial to continue.

.. _autofixing:

Support for Plugins that Autofix Errors
+++++++++++++++++++++++++++++++++++++++

Flake8 should enable people writing plugins for both core Flake8 checkers and
third-party checkers that allow the code to be automatically fixed. The trick
is in how to do this.

Once Flake8 has control over running plugins and treats pep8, flake8, and
mccabe as "plugins", it will aggregate the errors returned by all of the
plugins and be able to "notify" other plugins that have chosen to listen for
errors so those plugins can auto-fix the problems in the file.

We should also be considerate of allowing these plugins to be composable. Each
plugin should have a way of defining its capabilities.

See https://gitlab.com/pycqa/flake8/issues/84

.. note:: Will probably need a Trie implementation for this

What we *might* want is for a autofix plugin to register something like

::

    'flake8.autofix_extension': [
        'E1 = my_fixer.E1Listener',
        'E2 = my_fixer.E2Listener',
    ]

This means that the notifer would need to take an error code like ``E111`` and
then notify anything listening for ``E111``, ``E11``, ``E1``, and ``E``.

.. _reporter-plugins:

Support for Plugins that Format Output
++++++++++++++++++++++++++++++++++++++

Flake8 currently supports formatting output via pep8's ``--format`` option.
This works but is fundamentally a bit limiting. Allowing users to replace or
compose formatters would allow for certain formatters to highlight more
important information over less important information as the user deems
necessary.

See https://gitlab.com/pycqa/flake8/issues/66

.. _report-generation:

Support for Report Generation
+++++++++++++++++++++++++++++

Flake8 should support pluggable report formats. See also pluggable report
formats for https://github.com/openstack/bandit

Report generation plugins may also choose to implement a way to store previous
runs of flake8. As such these plugins should be designed to be composable as
well.

.. _options-passing:

Support for Plugins Require Parsed Options
++++++++++++++++++++++++++++++++++++++++++

Plugins currently are able to use ``add_options`` and ``parse_options``
classmethods to register and retrieve options information. This is admittedly
a little awkward and could be improved, but should at least be preserved in
this rewrite.

See potential improvements as a result of
https://gitlab.com/pycqa/flake8/issues/88

.. _plugin-default-ignore:

Support for Plugins Specifying Default Ignore list
++++++++++++++++++++++++++++++++++++++++++++++++++

Plugins currently have no way of extending the default ignore list. This means
they have to hard-code checks to auto-ignore errors.

.. _options:

Better Options Support
----------------------

Currently there are some options handled by pep8 that are handled poorly.
Further, the way the options work is confusing to some, e.g., when specifying
``--ignore``, users do not expect it to override the ``DEFAULT_IGNORE`` list.
Users also don't expect ``--ignore`` and ``--select`` to step on each other's
toes.

.. _better-select-ignore:

Support for Better Select/Ignore Handling
+++++++++++++++++++++++++++++++++++++++++

Currently ``--select`` and ``--ignore`` cause one or the other to be ignored.
Users presently cannot specify both for granularity. This should be
significantly improved.

Further, new tools have developed ``--add-select`` and ``--add-ignore`` which
allows an add-only interface. This seems to be a good direction to follow.
Flake8 should support this.

See https://github.com/PyCQA/pep8/issues/390

.. _standard-in:

Better stdin support
--------------------

Currently, flake8 accepts input from standard-in to check. It also currently
monkey-patches pep8 to cache that value. It would be better if there was one
way to retrieve the stdin input for plugins. Flake8 should provide this
directly instead of pep8 providing it.

See
https://gitlab.com/pycqa/flake8/commit/41393c9b6de513ea169b61c175b71018e8a12336

.. _multiprocessing:

Multiprocessing Support
-----------------------

Flake8's existing multiprocessing support (and handling for different error
cases needs to persist through this redesign).

See:

- https://gitlab.com/pycqa/flake8/issues/8
- https://gitlab.com/pycqa/flake8/issues/17
- https://gitlab.com/pycqa/flake8/issues/44
- https://gitlab.com/pycqa/flake8/issues/74
