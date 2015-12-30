from flake8 import _trie


class Notifier(object):
    def __init__(self):
        """Initialize an empty notifier object."""
        self.listeners = _trie.Trie()

    def listeners_for(self, error_code):
        """Retrieve listeners for an error_code.

        The error code does not need to be a specific error code. For example,
        There may be listeners registered for E100, E101, E110, E112, and
        E126. If you wanted to get all listeners starting with 'E1' then you
        would pass 'E1' as the error code here.

        Example usage

        .. code-block:: python

            from flake8 import notifier

            n = notifier.Notifier()
            # register listeners
            for listener in n.listeners_for('E1'):
                listener.notify(...)

            for listener in n.listeners_for('W102'):
                listener.notify(...)
        """
        node = self.listeners.find(error_code)
        if node is None:
            return
        for listener in node.data:
            yield listener
        for child in node.traverse():
            for listener in child.data:
                yield listener

    def notify(self, error_code, *args, **kwargs):
        """Notify all listeners for the specified error code."""
        for listener in self.listeners_for(error_code):
            listener.notify(error_code, *args, **kwargs)

    def register_listener(self, error_code, listener):
        """Register a listener for a specific error_code."""
        self.listeners.add(error_code, listener)
