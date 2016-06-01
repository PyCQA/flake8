# -*- coding: utf-8 -*-
import os
import sys

try:
    import ast
    iter_child_nodes = ast.iter_child_nodes
except ImportError:   # Python 2.5
    import _ast as ast

    if 'decorator_list' not in ast.ClassDef._fields:
        # Patch the missing attribute 'decorator_list'
        ast.ClassDef.decorator_list = ()
        ast.FunctionDef.decorator_list = property(lambda s: s.decorators)

    def iter_child_nodes(node):
        """
        Yield all direct child nodes of *node*, that is, all fields that
        are nodes and all items of fields that are lists of nodes.
        """
        if not node._fields:
            return
        for name in node._fields:
            field = getattr(node, name, None)
            if isinstance(field, ast.AST):
                yield field
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, ast.AST):
                        yield item


class OrderedSet(list):
    """List without duplicates."""
    __slots__ = ()

    def add(self, value):
        if value not in self:
            self.append(value)


def is_windows():
    """Determine if the system is Windows."""
    return os.name == 'nt'


def is_using_stdin(paths):
    """Determine if we're running checks on stdin."""
    return '-' in paths


def warn_when_using_jobs(options):
    return (options.verbose and options.jobs and options.jobs.isdigit() and
            int(options.jobs) > 1)


def force_disable_jobs(styleguide):
    affected_mp_version = (sys.version_info <= (2, 7, 11) or
                           (3, 0) <= sys.version_info < (3, 2))
    return (is_windows() and affected_mp_version or
            is_using_stdin(styleguide.paths))


INT_TYPES = ('int', 'count')
BOOL_TYPES = ('store_true', 'store_false')
LIST_OPTIONS = ('select', 'ignore', 'exclude', 'enable_extensions')


def option_normalizer(value, option, option_name):
    if option.action in BOOL_TYPES:
        if str(value).upper() in ('1', 'T', 'TRUE', 'ON'):
            value = True
        if str(value).upper() in ('0', 'F', 'FALSE', 'OFF'):
            value = False
    elif option.type in INT_TYPES:
        value = int(value)
    elif option_name in LIST_OPTIONS:
        if isinstance(value, str):
            value = [opt.strip() for opt in value.split(',') if opt.strip()]

    return value
