# -*- coding: utf-8 -*-

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
