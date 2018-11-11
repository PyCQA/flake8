====================================
 Writing Plugins For Flake8 2 and 3
====================================

Plugins have existed for |Flake8| 2.x for a few years. There are a number of
these on PyPI already. While it did not seem reasonable for |Flake8| to attempt
to provide a backwards compatible shim for them, we did decide to try to
document the easiest way to write a plugin that's compatible across both
versions.

.. note::

    If your plugin does not register options, it *should* Just Work.

The **only two** breaking changes in |Flake8| 3.0 is the fact that we no
longer check the option parser for a list of strings to parse from a config
file and we no longer patch pep8 or pycodestyle's ``stdin_get_value``
functions. On |Flake8| 2.x, to have an option parsed from the configuration
files that |Flake8| finds and parses you would have to do something like:

.. code-block:: python

    parser.add_option('-X', '--example-flag', type='string',
                      help='...')
    parser.config_options.append('example-flag')

For |Flake8| 3.0, we have added *three* arguments to the
:meth:`~flake8.options.manager.OptionManager.add_option` method you will call
on the parser you receive:

- ``parse_from_config`` which expects ``True`` or ``False``

  When ``True``, |Flake8| will parse the option from the config files |Flake8|
  finds.

- ``comma_separated_list`` which expects ``True`` or ``False``

  When ``True``, |Flake8| will split the string intelligently and handle
  extra whitespace. The parsed value will be a list.

- ``normalize_paths`` which expects ``True`` or ``False``

  When ``True``, |Flake8| will:

  * remove trailing path separators (i.e., ``os.path.sep``)

  * return the absolute path for values that have the separator in them

All three of these options can be combined or used separately.


Parsing Options from Configuration Files
========================================

The example from |Flake8| 2.x now looks like:

.. code-block:: python

    parser.add_option('-X', '--example-flag', type='string',
                      parse_from_config=True,
                      help='...')


Parsing Comma-Separated Lists
=============================

Now let's imagine that the option we want to add is expecting a comma-separatd
list of values from the user (e.g., ``--select E123,W503,F405``). |Flake8| 2.x
often forced users to parse these lists themselves since pep8 special-cased
certain flags and left others on their own. |Flake8| 3.0 adds
``comma_separated_list`` so that the parsed option is already a list for
plugin authors. When combined with ``parse_from_config`` this means that users
can also do something like:

.. code-block:: ini

    example-flag =
        first,
        second,
        third,
        fourth,
        fifth

And |Flake8| will just return the list:

.. code-block:: python

    ["first", "second", "third", "fourth", "fifth"]


Normalizing Values that Are Paths
=================================

Finally, let's imagine that our new option wants a path or list of paths. To
ensure that these paths are semi-normalized (the way |Flake8| 2.x used to
work) we need only pass ``normalize_paths=True``. If you have specified
``comma_separated_list=True`` then this will parse the value as a list of
paths that have been normalized. Otherwise, this will parse the value
as a single path.


Option Handling on Flake8 2 and 3
=================================

To ease the transition, the |Flake8| maintainers have released
`flake8-polyfill`_. |polyfill| provides a convenience function to help users
transition between Flake8 2 and 3 without issue. For example, if your plugin
has to work on Flake8 2.x and 3.x but you want to take advantage of some of
the new options to ``add_option``, you can do

.. code-block:: python

    from flake8_polyfill import options


    class MyPlugin(object):
        @classmethod
        def add_options(cls, parser):
            options.register(
                parser,
                '--application-names', default='', type='string',
                help='Names of the applications to be checked.',
                parse_from_config=True,
                comma_separated_list=True,
            )
            options.register(
                parser,
                '--style-name', default='', type='string',
                help='The name of the style convention you want to use',
                parse_from_config=True,
            )
            options.register(
                parser,
                '--application-paths', default='', type='string',
                help='Locations of the application code',
                parse_from_config=True,
                comma_separated_list=True,
                normalize_paths=True,
            )

        @classmethod
        def parse_options(cls, parsed_options):
            cls.application_names = parsed_options.application_names
            cls.style_name = parsed_options.style_name
            cls.application_paths = parsed_options.application_paths

|polyfill| will handle these extra options using *callbacks* to the option
parser. The project has direct replications of the functions that |Flake8|
uses to provide the same functionality. This means that the values you receive
should be identically parsed whether you're using Flake8 2.x or 3.x.

.. autofunction:: flake8_polyfill.options.register


Standard In Handling on Flake8 2.5, 2.6, and 3
==============================================

After releasing |Flake8| 2.6, handling standard-in became a bit trickier for
some plugins. |Flake8| 2.5 and earlier had started monkey-patching pep8's
``stdin_get_value`` function. 2.6 switched to pycodestyle and only
monkey-patched that. 3.0 has its own internal implementation and uses that but
does not directly provide anything for plugins using pep8 and pycodestyle's
``stdin_get_value`` function. |polyfill| provides this functionality for
plugin developers via its :mod:`flake8_polyfill.stdin` module.

If a plugin needs to read the content from stdin, it can do the following:

.. code-block:: python

    from flake8_polyfill import stdin

    stdin.monkey_patch('pep8')  # To monkey-patch only pep8
    stdin.monkey_patch('pycodestyle')  # To monkey-patch only pycodestyle
    stdin.monkey_patch('all')  # To monkey-patch both pep8 and pycodestyle


Further, when using ``all``, |polyfill| does not require both packages to be
installed but will attempt to monkey-patch both and will silently ignore the
fact that pep8 or pycodestyle is not installed.

.. autofunction:: flake8_polyfill.stdin.monkey_patch


.. links
.. _flake8-polyfill: https://pypi.org/project/flake8-polyfill/

.. |polyfill| replace:: ``flake8-polyfill``
