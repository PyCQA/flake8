"""Tests for the flake8.style_guide.StyleGuide class."""
import optparse

import mock
import pytest

from flake8 import style_guide
from flake8.formatting import base
from flake8.plugins import notifier


def create_options(**kwargs):
    """Create and return an instance of optparse.Values."""
    kwargs.setdefault('select', [])
    kwargs.setdefault('extended_default_select', [])
    kwargs.setdefault('ignore', [])
    kwargs.setdefault('disable_noqa', False)
    kwargs.setdefault('enable_extensions', [])
    return optparse.Values(kwargs)


@pytest.mark.parametrize('select_list,ignore_list,error_code', [
    (['E111', 'E121'], [], 'E111'),
    (['E111', 'E121'], [], 'E121'),
    (['E11', 'E121'], ['E1'], 'E112'),
    (['E41'], ['E2', 'E12', 'E4'], 'E410'),
])
def test_handle_error_notifies_listeners(select_list, ignore_list, error_code):
    """Verify that error codes notify the listener trie appropriately."""
    listener_trie = mock.create_autospec(notifier.Notifier, instance=True)
    formatter = mock.create_autospec(base.BaseFormatter, instance=True)
    guide = style_guide.StyleGuide(create_options(select=select_list,
                                                  ignore=ignore_list),
                                   listener_trie=listener_trie,
                                   formatter=formatter)

    with mock.patch('linecache.getline', return_value=''):
        guide.handle_error(error_code, 'stdin', 1, 0, 'error found')
    error = style_guide.Violation(
        error_code, 'stdin', 1, 1, 'error found', None)
    listener_trie.notify.assert_called_once_with(error_code, error)
    formatter.handle.assert_called_once_with(error)


def test_handle_error_does_not_raise_type_errors():
    """Verify that we handle our inputs better."""
    listener_trie = mock.create_autospec(notifier.Notifier, instance=True)
    formatter = mock.create_autospec(base.BaseFormatter, instance=True)
    guide = style_guide.StyleGuide(create_options(select=['T111'], ignore=[]),
                                   listener_trie=listener_trie,
                                   formatter=formatter)

    assert 1 == guide.handle_error(
        'T111', 'file.py', 1, None, 'error found', 'a = 1'
    )


@pytest.mark.parametrize('select_list,ignore_list,error_code', [
    (['E111', 'E121'], [], 'E122'),
    (['E11', 'E12'], [], 'E132'),
    (['E2', 'E12'], [], 'E321'),
    (['E2', 'E12'], [], 'E410'),
    (['E111', 'E121'], ['E2'], 'E122'),
    (['E11', 'E12'], ['E13'], 'E132'),
    (['E1', 'E3'], ['E32'], 'E321'),
    (['E4'], ['E2', 'E12', 'E41'], 'E410'),
    (['E111', 'E121'], [], 'E112'),
])
def test_handle_error_does_not_notify_listeners(select_list, ignore_list,
                                                error_code):
    """Verify that error codes notify the listener trie appropriately."""
    listener_trie = mock.create_autospec(notifier.Notifier, instance=True)
    formatter = mock.create_autospec(base.BaseFormatter, instance=True)
    guide = style_guide.StyleGuide(create_options(select=select_list,
                                                  ignore=ignore_list),
                                   listener_trie=listener_trie,
                                   formatter=formatter)

    with mock.patch('linecache.getline', return_value=''):
        guide.handle_error(error_code, 'stdin', 1, 1, 'error found')
    assert listener_trie.notify.called is False
    assert formatter.handle.called is False
