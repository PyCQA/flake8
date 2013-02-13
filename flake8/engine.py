# -*- coding: utf-8 -*-
import pep8

from flake8 import __version__
from flake8.util import OrderedSet


def _register_extensions():
    """Register all the extensions."""
    extensions = OrderedSet()
    extensions.add(('pep8', pep8.__version__))
    parser_hooks = []
    options_hooks = []
    try:
        from pkg_resources import iter_entry_points
    except ImportError:
        pass
    else:
        for entry in iter_entry_points('flake8.extension'):
            checker = entry.load()
            pep8.register_check(checker, codes=[entry.name])
            extensions.add((checker.name, checker.version))
            if hasattr(checker, 'add_options'):
                parser_hooks.append(checker.add_options)
            if hasattr(checker, 'parse_options'):
                options_hooks.append(checker.parse_options)
    return extensions, parser_hooks, options_hooks


def get_parser():
    (extensions, parser_hooks, options_hooks) = _register_extensions()
    details = ', '.join(['%s: %s' % ext for ext in extensions])
    parser = pep8.get_parser('flake8', '%s (%s)' % (__version__, details))
    for opt in ('--repeat', '--testsuite', '--doctest'):
        try:
            parser.remove_option(opt)
        except ValueError:
            pass
    parser.add_option('--exit-zero', action='store_true',
                      help="exit with code 0 even if there are errors")
    for parser_hook in parser_hooks:
        parser_hook(parser)
    parser.add_option('--install-hook', default=False, action='store_true',
                      help='Install the appropriate hook for this '
                      'repository.', dest='install_hook')
    return parser, options_hooks


def get_style_guide(**kwargs):
    """Parse the options and configure the checker."""
    kwargs['parser'], options_hooks = get_parser()
    styleguide = pep8.StyleGuide(**kwargs)
    options = styleguide.options
    for options_hook in options_hooks:
        options_hook(options)
    return styleguide
