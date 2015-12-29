from flake8 import _trie


class Notifier(object):
    def __init__(self):
        self.listeners = _trie.Trie()

    def listeners_for(self, error_code):
        node = self.listeners.find(error_code)
        for listener in node.data:
            yield listener
        if node.children:
            for child in node.traverse():
                for listener in child.data:
                    yield listener

    def notify(self, error_code, *args, **kwargs):
        for listener in self.listeners_for(error_code):
            listener.notify(*args, **kwargs)

    def register_listener(self, error_code, listener):
        self.listeners.add(error_code, listener)
