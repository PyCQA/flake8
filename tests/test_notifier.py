import pytest

from flake8 import notifier

class _Listener(object):
    def __init__(self, error_code):
        self.error_code = error_code
        self.was_notified = False

    def notify(self, error_code, *args, **kwargs):
        assert self.error_code == error_code
        self.was_notified = True


class TestNotifier(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.notifier = notifier.Notifier()
        self.listener_map = {}

        for i in range(10):
            for j in range(30):
                error_code = 'E{0}{1:02d}'.format(i, j)
                listener = _Listener(error_code)
                self.listener_map[error_code] = listener
                self.notifier.register_listener(error_code, listener)

    def test_notify_a_single_error_code(self):
        """Show that we notify a specific error code."""
        self.notifier.notify('E111', 'extra', 'args')
        assert self.listener_map['E111'].was_notified is True
