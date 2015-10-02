# -*- coding: utf-8 -*-
import os

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
    return is_windows() or is_using_stdin(styleguide.paths)


def option_normalizer(value):
    if str(value).upper() in ('1', 'T', 'TRUE', 'ON'):
        value = True
    if str(value).upper() in ('0', 'F', 'FALSE', 'OFF'):
        value = False

    if isinstance(value, str):
        value = [opt.strip() for opt in value.split(',') if opt.strip()]

    return value
