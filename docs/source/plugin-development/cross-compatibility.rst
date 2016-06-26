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

The **only** breaking change in |Flake8| 3.0 is the fact that we no longer
check the option parser for a list of strings to parse from a config file. On
|Flake8| 2.x, to have an option parsed from the configuration files that
|Flake8| finds and parses you would have to do something like:

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

So, in conclusion, we can now write our plugin that relies on registering
options with |Flake8| and have it work on |Flake8| 2.x and 3.x.

.. code-block:: python

    import optparse

    option_args = ('-X', '--example-flag')
    option_kwargs = {
        'type': 'string',
        'parse_from_config': True,
        'help': '...',
    }
    try:
        # Flake8 3.x registration
        parser.add_option(*option_args, **option_kwargs)
    except (optparse.OptionError, TypeError):
        # Flake8 2.x registration
        parse_from_config = option_kwargs.pop('parse_from_config', False)
        parser.add_option(*option_args, **option_kwargs)
        if parse_from_config:
            parser.config_options.append(option_args[-1].lstrip('-'))


Or, you can write a tiny helper function:

.. code-block:: python

    import optparse

    def register_opt(parser, *args, **kwargs):
        try:
            # Flake8 3.x registration
            parser.add_option(*args, **kwargs)
        except (optparse.OptionError, TypeError):
            # Flake8 2.x registration
            parse_from_config = kwargs.pop('parse_from_config', False)
            kwargs.pop('comma_separated_list', False)
            kwargs.pop('normalize_paths', False)
            parser.add_option(*args, **kwargs)
            if parse_from_config:
                parser.config_options.append(args[-1].lstrip('-'))

.. code-block:: python

    @classmethod
    def register_options(cls, parser):
        register_opt(parser, '-X', '--example-flag', type='string',
                     parse_from_config=True, help='...')

The transition period is admittedly not fantastic, but we believe that this
is a worthwhile change for plugin developers going forward. We also hope to
help with the transition phase for as many plugins as we can manage.
