# -*- coding: utf-8 -*-
from __future__ import with_statement
import os.path
import re

__all__ = ['ast', 'iter_child_nodes', 'OrderedSet', 'skip_file']

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

_NOQA = re.compile(r'flake8[:=]\s*noqa', re.I | re.M)


def skip_file(path, source=None):
    """Returns True if this header is found in path

    # flake8: noqa
    """
    if os.path.isfile(path):
        with open(path) as f:
            source = f.read()
    elif not source:
        return False

    return _NOQA.search(source) is not None
