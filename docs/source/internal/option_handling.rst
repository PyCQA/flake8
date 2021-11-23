Option and Configuration Handling
=================================

Option Management
-----------------

Command-line options are often also set in configuration files for |Flake8|.
While not all options are meant to be parsed from configuration files, many
default options are also parsed from configuration files as well as
most plugin options.

In |Flake8| 2, plugins received a :class:`optparse.OptionParser` instance and
called :meth:`optparse.OptionParser.add_option` to register options. If the
plugin author also wanted to have that option parsed from config files they
also had to do something like:

.. code-block:: python

    parser.config_options.append('my_config_option')
    parser.config_options.extend(['config_opt1', 'config_opt2'])

This was previously undocumented and led to a lot of confusion about why
registered options were not automatically parsed from configuration files.

Since |Flake8| 3 was rewritten from scratch, we decided to take a different
approach to configuration file parsing. Instead of needing to know about an
undocumented attribute that pep8 looks for, |Flake8| 3 now accepts a parameter
to ``add_option``, specifically ``parse_from_config`` which is a boolean
value.

|Flake8| does this by creating its own abstractions on top of :mod:`argparse`.
The first abstraction is the :class:`flake8.options.manager.Option` class. The
second is the :class:`flake8.options.manager.OptionManager`. In fact, we add
three new parameters:

- ``parse_from_config``

- ``comma_separated_list``

- ``normalize_paths``

The last two are not specifically for configuration file handling, but they
do improve that dramatically. We found that there were options that, when
specified in a configuration file, often necessitated being split across
multiple lines and those options were almost always comma-separated. For
example, let's consider a user's list of ignored error codes for a project:

.. code-block:: ini

    [flake8]
    ignore =
        # Reasoning
        E111,
        # Reasoning
        E711,
        # Reasoning
        E712,
        # Reasoning
        E121,
        # Reasoning
        E122,
        # Reasoning
        E123,
        # Reasoning
        E131,
        # Reasoning
        E251

It makes sense here to allow users to specify the value this way, but, the
standard library's :class:`configparser.RawConfigParser` class does returns a
string that looks like

.. code-block:: python

    "\nE111,  \nE711,  \nE712,  \nE121,  \nE122,  \nE123,  \nE131,  \nE251  "

This means that a typical call to :meth:`str.split` with ``','`` will not be
sufficient here. Telling |Flake8| that something is a comma-separated list
(e.g., ``comma_separated_list=True``) will handle this for you. |Flake8| will
return:

.. code-block:: python

    ["E111", "E711", "E712", "E121", "E122", "E123", "E131", "E251"]

Next let's look at how users might like to specify their ``exclude`` list.
Presently OpenStack's Nova project has this line in their `tox.ini`_:

.. code-block:: ini

    exclude = .venv,.git,.tox,dist,doc,*openstack/common/*,*lib/python*,*egg,build,tools/xenserver*,releasenotes

We think we can all agree that this would be easier to read like this:

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

Now let's look at how this will actually be used. Most plugin developers
will receive an instance of :class:`~flake8.options.manager.OptionManager` so
to ease the transition we kept the same API as the
:class:`optparse.OptionParser` object. The only difference is that
:meth:`~flake8.options.manager.OptionManager.add_option` accepts the three
extra arguments we highlighted above.

.. _tox.ini:
    https://github.com/openstack/nova/blob/3eb190c4cfc0eefddac6c2cc1b94a699fb1687f8/tox.ini#L155

Configuration File Management
-----------------------------

In |Flake8| 2, configuration file discovery and management was handled by
pep8.  In pep8's 1.6 release series, it drastically broke how discovery and
merging worked (as a result of trying to improve it). To avoid a dependency
breaking |Flake8| again in the future, we have created our own discovery and
management in 3.0.0. In 4.0.0 we have once again changed how this works and we
removed support for user-level config files.

- Project files (files stored in the current directory) are read next and
  merged on top of the user file. In other words, configuration in project
  files takes precedence over configuration in user files.

- **New in 3.0.0** The user can specify ``--append-config <path-to-file>``
  repeatedly to include extra configuration files that should be read and
  take precedence over user and project files.

- **New in 3.0.0** The user can specify ``--config <path-to-file>`` to so this
  file is the only configuration file used. This is a change from |Flake8| 2
  where pep8 would simply merge this configuration file into the configuration
  generated by user and project files (where this takes precedence).

- **New in 3.0.0** The user can specify ``--isolated`` to disable
  configuration via discovered configuration files.

To facilitate the configuration file management, we've taken a different
approach to discovery and management of files than pep8. In pep8 1.5, 1.6, and
1.7 configuration discovery and management was centralized in `66 lines of
very terse python`_ which was confusing and not very explicit. The terseness
of this function (|Flake8| 3.0.0's authors believe) caused the confusion and
problems with pep8's 1.6 series. As such, |Flake8| has separated out
discovery, management, and merging into a module to make reasoning about each
of these pieces easier and more explicit (as well as easier to test).

Configuration file discovery and raw ini reading is managed by
:func:`~flake8.options.config.load_config`.  This produces a loaded
:class:`~configparser.RawConfigParser` and a config directory (which will be
used later to normalize paths).

Next, :func:`~flake8.options.config.parse_config` parses options using the
types in the ``OptionManager``.

Most of this is done in :func:`~flake8.options.aggregator.aggregate_options`.

Aggregating Configuration File and Command Line Arguments
---------------------------------------------------------

:func:`~flake8.options.aggregator.aggregate_options` accepts an instance of
:class:`~flake8.options.manager.OptionManager` and does the work to parse the
command-line arguments.

After parsing the configuration file, we determine the default ignore list. We
use the defaults from the OptionManager and update those with the parsed
configuration files. Finally we parse the user-provided options one last time
using the option defaults and configuration file values as defaults. The
parser merges on the command-line specified arguments for us so we have our
final, definitive, aggregated options.

.. _66 lines of very terse python:
    https://github.com/PyCQA/pep8/blob/b8088a2b6bc5b76bece174efad877f764529bc74/pep8.py#L1981..L2047

API Documentation
-----------------

.. autofunction:: flake8.options.aggregator.aggregate_options

.. autoclass:: flake8.options.manager.Option
    :members: __init__, normalize, to_argparse

.. autoclass:: flake8.options.manager.OptionManager
    :members:
    :special-members:

.. autofunction:: flake8.options.config.load_config

.. autofunction:: flake8.options.config.parse_config
