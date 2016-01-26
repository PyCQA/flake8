Option and Configuration Handling
=================================

Option Management
-----------------

Command-line options are often also set in configuration files for Flake8.
While not all options are meant to be parsed from configuration files, many
default options are also parsed from configuration files as are most plugin
options.

In Flake8 2, plugins received a :class:`optparse.OptionParser` instance and
called :meth:`optparse.OptionParser.add_option` to register options. If the
plugin author also wanted to have that option parsed from config files they
also had to do something like:

.. code-block:: python

    parser.config_options.append('my_config_option')
    parser.config_options.extend(['config_opt1', 'config_opt2'])

This was previously undocumented and led to a lot of confusion as to why
registered options were not automatically parsed from configuration files.

Since Flake8 3 was rewritten from scratch, we decided to take a different
approach to configuration file parsing. Instead of needing to know about an
undocumented attribute that pep8 looks for, Flake8 3 now accepts a parameter
to ``add_option``, specifically ``parse_from_config`` which is a boolean
value.

Flake8 does this by creating its own abstractions on top of :mod:`optparse`.
The first abstraction is the :class:`flake8.options.manager.Option` class. The
second is the :class:`flake8.options.manager.OptionManager`. In fact, we add
three new parameters:

- ``parse_from_config``

- ``comma_separated_list``

- ``normalize_paths``

The last two are not specifically for configuration file handling, but they
do improve that dramatically. We found that there were options that when
specified in a configuration file, lended themselves to being split across
multiple lines and those options were almost always comma-separated. For
example, let's consider a user's list of ignored error codes for a project:

.. code-block:: ini

    [flake8]
    ignore =
        E111,  # Reasoning
        E711,  # Reasoning
        E712,  # Reasoning
        E121,  # Reasoning
        E122,  # Reasoning
        E123,  # Reasoning
        E131,  # Reasoning
        E251   # Reasoning

It makes sense here to allow users to specify the value this way, but, the
standard libary's :class:`configparser.RawConfigParser` class does returns a
string that looks like

.. code-block:: python

    "\nE111,  \nE711,  \nE712,  \nE121,  \nE122,  \nE123,  \nE131,  \nE251  "

This means that a typical call to :meth:`str.split` with ``','`` will not be
sufficient here. Telling Flake8 that something is a comma-separated list
(e.g., ``comma_separated_list=True``) will handle this for you. Flake8 will
return:

.. code-block:: python

    ["E111", "E711", "E712", "E121", "E122", "E123", "E131", "E251"]

Next let's look at how users might like to specify their ``exclude`` list.
Presently OpenStack's Nova project has this line in their `tox.ini`_:

.. code-block:: ini

    exclude = .venv,.git,.tox,dist,doc,*openstack/common/*,*lib/python*,*egg,build,tools/xenserver*,releasenotes

I think we can all agree that this would be easier to read like this:

.. code-block:: ini

    exclude =
        .venv,
        .git,
        .tox,
        dist,
        doc,
        *openstack/common/*,
        *lib/python*,
        *egg,
        build,
        tools/xenserver*,
        releasenotes

In this case, since these are actually intended to be paths, we would specify
both ``comma_separated_list=True`` and ``normalize_paths=True`` because we
want the paths to be provided to us with some consistency (either all absolute
paths or not).

Now let's look at how this would actually be utilized. Most plugin developers
will receive an instance of :class:`~flake8.options.manager.OptionManager` so
to ease the transition we kept the same API as the
:class:`optparse.OptionParser` object. The only difference is that
:meth:`~flake8.options.manager.OptionManager.add_option` accepts the three
extra arguments we highlighted above.

.. _tox.ini:
    https://github.com/openstack/nova/blob/3eb190c4cfc0eefddac6c2cc1b94a699fb1687f8/tox.ini#L155

Configuration File Management
-----------------------------

.. todo:: Add notes about Config File Management

API Documentation
-----------------

.. autoclass:: flake8.options.manager.Option
    :members: __init__, normalize, to_optparse

.. autoclass:: flake8.options.manager.OptionManager
    :members:
    :special-members:

.. autoclass:: flake8.options.config.MergedConfigParser
    :members:
