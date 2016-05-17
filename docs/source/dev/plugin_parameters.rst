====================================
 Receiving Information For A Plugin
====================================

Plugins to Flake8 have a great deal of information that they can request from
a :class:`~flake8.processor.FileProcessor` instance. Historically, Flake8 has
supported two types of plugins:

#. classes that accept parsed abstract syntax trees (ASTs)

#. functions that accept a range of arguments

Flake8 now does not distinguish between the two types of plugins. Any plugin
can accept either an AST or a range of arguments. Further, any plugin that has
certain callable attributes can also register options and receive parsed
options.

Indicating Desired Data
=======================

Flake8 inspects the plugin's signature to determine what parameters it expects
using :func:`flake8.utils.parameters_for`.
:attr:`flake8.plugins.manager.Plugin.parameters` caches the values so that
each plugin makes that fairly expensive call once per plugin. When processing 
a file, a plugin can ask for any of the following:

- :attr:`~flake8.processor.FileProcessor.blank_before`
- :attr:`~flake8.processor.FileProcessor.blank_lines`
- :attr:`~flake8.processor.FileProcessor.checker_state`
- :attr:`~flake8.processor.FileProcessor.indect_char`
- :attr:`~flake8.processor.FileProcessor.indent_level`
- :attr:`~flake8.processor.FileProcessor.line_number`
- :attr:`~flake8.processor.FileProcessor.logical_line`
- :attr:`~flake8.processor.FileProcessor.max_line_length`
- :attr:`~flake8.processor.FileProcessor.multiline`
- :attr:`~flake8.processor.FileProcessor.noqa`
- :attr:`~flake8.processor.FileProcessor.previous_indent_level`
- :attr:`~flake8.processor.FileProcessor.previous_logical`
- :attr:`~flake8.processor.FileProcessor.tokens`
- :attr:`~flake8.processor.FileProcessor.total_lines`
- :attr:`~flake8.processor.FileProcessor.verbose`

Alternatively, a plugin can accept ``tree`` and ``filename``.
``tree`` will be a parsed abstract syntax tree that will be used by plugins
like PyFlakes and McCabe.

Finally, any plugin that has callable attributes ``provide_options`` and
``register_options`` can parse option information and register new options.
