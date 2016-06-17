"""Unit tests for the Notifier object."""
import pytest

from flake8.plugins import notifier


class _Listener(object):
    def __init__(self, error_code):
        self.error_code = error_code
        self.was_notified = False

    def notify(self, error_code, *args, **kwargs):
        assert error_code.startswith(self.error_code)
        self.was_notified = True


class TestNotifier(object):
    """Notifier unit tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up each TestNotifier instance."""
        self.notifier = notifier.Notifier()
        self.listener_map = {}

        def add_listener(error_code):
            listener = _Listener(error_code)
            self.listener_map[error_code] = listener
            self.notifier.register_listener(error_code, listener)

        for i in range(10):
            add_listener('E{0}'.format(i))
            for j in range(30):
                add_listener('E{0}{1:02d}'.format(i, j))

    def test_notify(self):
        """Show that we notify a specific error code."""
        self.notifier.notify('E111', 'extra', 'args')
        assert self.listener_map['E111'].was_notified is True
        assert self.listener_map['E1'].was_notified is True

    @pytest.mark.parametrize('code', ['W123', 'W12', 'W1', 'W'])
    def test_no_listeners_for(self, code):
        """Show that we return an empty list of listeners."""
        assert list(self.notifier.listeners_for(code)) == []

    @pytest.mark.parametrize('code,expected', [
        ('E101', ['E101', 'E1']),
        ('E211', ['E211', 'E2']),
    ])
    def test_listeners_for(self, code, expected):
        """Verify that we retrieve the correct listeners."""
        assert ([l.error_code for l in self.notifier.listeners_for(code)] ==
                expected)
