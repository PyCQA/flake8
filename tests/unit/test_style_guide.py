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
    kwargs.setdefault('ignore', [])
    kwargs.setdefault('disable_noqa', False)
    return optparse.Values(kwargs)


@pytest.mark.parametrize('ignore_list,error_code', [
    (['E111', 'E121'], 'E111'),
    (['E111', 'E121'], 'E121'),
    (['E11', 'E12'], 'E121'),
    (['E2', 'E12'], 'E121'),
    (['E2', 'E12'], 'E211'),
])
def test_is_user_ignored_ignores_errors(ignore_list, error_code):
    """Verify we detect users explicitly ignoring an error."""
    guide = style_guide.StyleGuide(create_options(ignore=ignore_list),
                                   listener_trie=None,
                                   formatter=None)

    assert guide.is_user_ignored(error_code) is style_guide.Ignored.Explicitly


@pytest.mark.parametrize('ignore_list,error_code', [
    (['E111', 'E121'], 'E112'),
    (['E111', 'E121'], 'E122'),
    (['E11', 'E12'], 'W121'),
    (['E2', 'E12'], 'E112'),
    (['E2', 'E12'], 'E111'),
])
def test_is_user_ignored_implicitly_selects_errors(ignore_list, error_code):
    """Verify we detect users does not explicitly ignore an error."""
    guide = style_guide.StyleGuide(create_options(ignore=ignore_list),
                                   listener_trie=None,
                                   formatter=None)

    assert guide.is_user_ignored(error_code) is style_guide.Selected.Implicitly


@pytest.mark.parametrize('select_list,error_code', [
    (['E111', 'E121'], 'E111'),
    (['E111', 'E121'], 'E121'),
    (['E11', 'E12'], 'E121'),
    (['E2', 'E12'], 'E121'),
    (['E2', 'E12'], 'E211'),
])
def test_is_user_selected_selects_errors(select_list, error_code):
    """Verify we detect users explicitly selecting an error."""
    guide = style_guide.StyleGuide(create_options(select=select_list),
                                   listener_trie=None,
                                   formatter=None)

    assert (guide.is_user_selected(error_code) is
            style_guide.Selected.Explicitly)


def test_is_user_selected_implicitly_selects_errors():
    """Verify we detect users implicitly selecting an error."""
    select_list = []
    error_code = 'E121'
    guide = style_guide.StyleGuide(create_options(select=select_list),
                                   listener_trie=None,
                                   formatter=None)

    assert (guide.is_user_selected(error_code) is
            style_guide.Selected.Implicitly)


@pytest.mark.parametrize('select_list,error_code', [
    (['E111', 'E121'], 'E112'),
    (['E111', 'E121'], 'E122'),
    (['E11', 'E12'], 'E132'),
    (['E2', 'E12'], 'E321'),
    (['E2', 'E12'], 'E410'),
])
def test_is_user_selected_excludes_errors(select_list, error_code):
    """Verify we detect users implicitly excludes an error."""
    guide = style_guide.StyleGuide(create_options(select=select_list),
                                   listener_trie=None,
                                   formatter=None)

    assert guide.is_user_selected(error_code) is style_guide.Ignored.Implicitly


@pytest.mark.parametrize('select_list,ignore_list,error_code,expected', [
    (['E111', 'E121'], [], 'E111', style_guide.Decision.Selected),
    (['E111', 'E121'], [], 'E112', style_guide.Decision.Ignored),
    (['E111', 'E121'], [], 'E121', style_guide.Decision.Selected),
    (['E111', 'E121'], [], 'E122', style_guide.Decision.Ignored),
    (['E11', 'E12'], [], 'E132', style_guide.Decision.Ignored),
    (['E2', 'E12'], [], 'E321', style_guide.Decision.Ignored),
    (['E2', 'E12'], [], 'E410', style_guide.Decision.Ignored),
    (['E11', 'E121'], ['E1'], 'E112', style_guide.Decision.Selected),
    (['E111', 'E121'], ['E2'], 'E122', style_guide.Decision.Ignored),
    (['E11', 'E12'], ['E13'], 'E132', style_guide.Decision.Ignored),
    (['E1', 'E3'], ['E32'], 'E321', style_guide.Decision.Ignored),
    ([], ['E2', 'E12'], 'E410', style_guide.Decision.Selected),
    (['E4'], ['E2', 'E12', 'E41'], 'E410', style_guide.Decision.Ignored),
    (['E41'], ['E2', 'E12', 'E4'], 'E410', style_guide.Decision.Selected),
])
def test_should_report_error(select_list, ignore_list, error_code, expected):
    """Verify we decide when to report an error."""
    guide = style_guide.StyleGuide(create_options(select=select_list,
                                                  ignore=ignore_list),
                                   listener_trie=None,
                                   formatter=None)

    assert guide.should_report_error(error_code) is expected


@pytest.mark.parametrize('error_code,physical_line,expected_result', [
    ('E111', 'a = 1', False),
    ('E121', 'a = 1  # noqa: E111', False),
    ('E121', 'a = 1  # noqa: E111,W123,F821', False),
    ('E111', 'a = 1  # noqa: E111,W123,F821', True),
    ('W123', 'a = 1  # noqa: E111,W123,F821', True),
    ('E111', 'a = 1  # noqa: E11,W123,F821', True),
    ('E111', 'a = 1  # noqa, analysis:ignore', True),
    ('E111', 'a = 1  # noqa analysis:ignore', True),
    ('E111', 'a = 1  # noqa - We do not care', True),
])
def test_is_inline_ignored(error_code, physical_line, expected_result):
    """Verify that we detect inline usage of ``# noqa``."""
    guide = style_guide.StyleGuide(create_options(select=['E', 'W', 'F']),
                                   listener_trie=None,
                                   formatter=None)
    error = style_guide.Error(error_code, 'filename.py', 1, 1, 'error text',
                              None)
    # We want `None` to be passed as the physical line so we actually use our
    # monkey-patched linecache.getline value.

    with mock.patch('linecache.getline', return_value=physical_line):
        assert guide.is_inline_ignored(error) is expected_result


def test_disable_is_inline_ignored():
    """Verify that is_inline_ignored exits immediately if disabling NoQA."""
    guide = style_guide.StyleGuide(create_options(disable_noqa=True),
                                   listener_trie=None,
                                   formatter=None)
    error = style_guide.Error('E121', 'filename.py', 1, 1, 'error text',
                              'line')

    with mock.patch('linecache.getline') as getline:
        assert guide.is_inline_ignored(error) is False

    assert getline.called is False


@pytest.mark.parametrize('select_list,ignore_list,error_code', [
    (['E111', 'E121'], [], 'E111'),
    (['E111', 'E121'], [], 'E121'),
    (['E11', 'E121'], ['E1'], 'E112'),
    ([], ['E2', 'E12'], 'E410'),
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
    error = style_guide.Error(error_code, 'stdin', 1, 1, 'error found',
                              None)
    listener_trie.notify.assert_called_once_with(error_code, error)
    formatter.handle.assert_called_once_with(error)


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
