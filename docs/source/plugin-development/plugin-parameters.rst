.. _plugin-parameters:

==========================================
 Receiving Information For A Check Plugin
==========================================

Plugins to |Flake8| have a great deal of information that they can request
from a :class:`~flake8.processor.FileProcessor` instance. Historically,
|Flake8| has supported two types of plugins:

#. classes that accept parsed abstract syntax trees (ASTs)

#. functions that accept a range of arguments

|Flake8| now does not distinguish between the two types of plugins. Any plugin
can accept either an AST or a range of arguments. Further, any plugin that has
certain callable attributes can also register options and receive parsed
options.


Indicating Desired Data
=======================

|Flake8| inspects the plugin's signature to determine what parameters it
expects using :func:`flake8.utils.parameters_for`.
:attr:`flake8.plugins.manager.Plugin.parameters` caches the values so that
each plugin makes that fairly expensive call once per plugin. When processing
a file, a plugin can ask for any of the following:

- :attr:`~flake8.processor.FileProcessor.blank_before`
- :attr:`~flake8.processor.FileProcessor.blank_lines`
- :attr:`~flake8.processor.FileProcessor.checker_state`
- :attr:`~flake8.processor.FileProcessor.indent_char`
- :attr:`~flake8.processor.FileProcessor.indent_level`
- :attr:`~flake8.processor.FileProcessor.line_number`
- :attr:`~flake8.processor.FileProcessor.logical_line`
- :attr:`~flake8.processor.FileProcessor.multiline`
- :attr:`~flake8.processor.FileProcessor.noqa`
- :attr:`~flake8.processor.FileProcessor.previous_indent_level`
- :attr:`~flake8.processor.FileProcessor.previous_logical`
- :attr:`~flake8.processor.FileProcessor.tokens`

Some properties are set once per file being processed:

- :attr:`~flake8.processor.FileProcessor.filename`
- :attr:`~flake8.processor.FileProcessor.lines`
- :attr:`~flake8.processor.FileProcessor.max_line_length`
- :attr:`~flake8.processor.FileProcessor.total_lines`
- :attr:`~flake8.processor.FileProcessor.verbose`

These parameters can also be supplied to plugins working on each line
separately. Additionally, plugins called once per file can also accept ``tree``
which is not supplied as a parameter of
:class:`~flake8.processor.FileProcessor`, which will be a parsed abstract
syntax tree. It is used by plugins like PyFlakes and McCabe.


Registering Options
===================

Any plugin that has callable attributes ``provide_options`` and
``register_options`` can parse option information and register new options.

Your ``register_options`` function should expect to receive an instance of
|OptionManager|. An |OptionManager| instance behaves very similarly to
:class:`optparse.OptionParser`. It, however, uses the layer that |Flake8| has
developed on top of :mod:`optparse` to also handle configuration file parsing.
:meth:`~flake8.options.manager.OptionManager.add_option` creates an |Option|
which accepts the same parameters as :mod:`optparse` as well as three extra
boolean parameters:

- ``parse_from_config``

  The command-line option should also be parsed from config files discovered
  by |Flake8|.

  .. note::

      This takes the place of appending strings to a list on the
      :class:`optparse.OptionParser`.

- ``comma_separated_list``

  The value provided to this option is a comma-separated list. After parsing
  the value, it should be further broken up into a list. This also allows us
  to handle values like:

  .. code::

      E123,E124,
      E125,
        E126

- ``normalize_paths``

  The value provided to this option is a path. It should be normalized to be
  an absolute path. This can be combined with ``comma_separated_list`` to
  allow a comma-separated list of paths.

Each of these options works individually or can be combined. Let's look at a
couple examples from |Flake8|. In each example, we will have
``option_manager`` which is an instance of |OptionManager|.

.. code-block:: python

    option_manager.add_option(
        '--max-line-length', type='int', metavar='n',
        default=defaults.MAX_LINE_LENGTH, parse_from_config=True,
        help='Maximum allowed line length for the entirety of this run. '
             '(Default: %default)',
    )

Here we are adding the ``--max-line-length`` command-line option which is
always an integer and will be parsed from the configuration file. Since we
provide a default, we take advantage of :mod:`optparse`\ 's willingness to
display that in the help text with ``%default``.

.. code-block:: python

    option_manager.add_option(
        '--select', metavar='errors', default='',
        parse_from_config=True, comma_separated_list=True,
        help='Comma-separated list of errors and warnings to enable.'
             ' For example, ``--select=E4,E51,W234``. (Default: %default)',
    )

In adding the ``--select`` command-line option, we're also indicating to the
|OptionManager| that we want the value parsed from the config files and parsed
as a comma-separated list.

.. code-block:: python

    option_manager.add_option(
        '--exclude', metavar='patterns', default=defaults.EXCLUDE,
        comma_separated_list=True, parse_from_config=True,
        normalize_paths=True,
        help='Comma-separated list of files or directories to exclude.'
             '(Default: %default)',
    )

Finally, we show an option that uses all three extra flags. Values from
``--exclude`` will be parsed from the config, converted from a comma-separated
list, and then each item will be normalized.

For information about other parameters to
:meth:`~flake8.options.manager.OptionManager.add_option` refer to the
documentation of :mod:`optparse`.


Accessing Parsed Options
========================

When a plugin has a callable ``provide_options`` attribute, |Flake8| will call
it and attempt to provide the |OptionManager| instance, the parsed options
which will be an instance of :class:`optparse.Values`, and the extra arguments
that were not parsed by the |OptionManager|. If that fails, we will just pass
the :class:`optparse.Values`. In other words, your ``provide_options``
callable will have one of the following signatures:

.. code-block:: python

    def provide_options(option_manager, options, args):
        pass
    # or
    def provide_options(options):
        pass

.. substitutions
.. |OptionManager| replace:: :class:`~flake8.options.manager.OptionManager`
.. |Option| replace:: :class:`~flake8.options.manager.Option`
