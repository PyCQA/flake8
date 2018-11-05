"""Tests for our debugging module."""
import entrypoints
import mock
import pytest

from flake8.main import debug
from flake8.options import manager


def test_dependencies():
    """Verify that we format our dependencies appropriately."""
    expected = [{'dependency': 'entrypoints',
                 'version': entrypoints.__version__}]
    assert expected == debug.dependencies()


@pytest.mark.parametrize('plugins, expected', [
    ([], []),
    ([manager.PluginVersion('pycodestyle', '2.0.0', False)],
        [{'plugin': 'pycodestyle', 'version': '2.0.0', 'is_local': False}]),
    ([manager.PluginVersion('pycodestyle', '2.0.0', False),
      manager.PluginVersion('mccabe', '0.5.9', False)],
        [{'plugin': 'mccabe', 'version': '0.5.9', 'is_local': False},
         {'plugin': 'pycodestyle', 'version': '2.0.0', 'is_local': False}]),
    ([manager.PluginVersion('pycodestyle', '2.0.0', False),
      manager.PluginVersion('my-local', '0.0.1', True),
      manager.PluginVersion('mccabe', '0.5.9', False)],
        [{'plugin': 'mccabe', 'version': '0.5.9', 'is_local': False},
         {'plugin': 'my-local', 'version': '0.0.1', 'is_local': True},
         {'plugin': 'pycodestyle', 'version': '2.0.0', 'is_local': False}]),
])
def test_plugins_from(plugins, expected):
    """Test that we format plugins appropriately."""
    option_manager = mock.Mock(registered_plugins=set(plugins))
    assert expected == debug.plugins_from(option_manager)


@mock.patch('platform.python_implementation', return_value='CPython')
@mock.patch('platform.python_version', return_value='3.5.3')
@mock.patch('platform.system', return_value='Linux')
def test_information(system, pyversion, pyimpl):
    """Verify that we return all the information we care about."""
    expected = {
        'version': '3.1.0',
        'plugins': [{'plugin': 'mccabe', 'version': '0.5.9',
                     'is_local': False},
                    {'plugin': 'pycodestyle', 'version': '2.0.0',
                     'is_local': False}],
        'dependencies': [{'dependency': 'entrypoints',
                          'version': entrypoints.__version__}],
        'platform': {
            'python_implementation': 'CPython',
            'python_version': '3.5.3',
            'system': 'Linux',
        },
    }
    option_manager = mock.Mock(
        registered_plugins={
            manager.PluginVersion('pycodestyle', '2.0.0', False),
            manager.PluginVersion('mccabe', '0.5.9', False),
        },
        version='3.1.0',
    )
    assert expected == debug.information(option_manager)
    pyimpl.assert_called_once_with()
    pyversion.assert_called_once_with()
    system.assert_called_once_with()


@mock.patch('flake8.main.debug.print')
@mock.patch('flake8.main.debug.information', return_value={})
@mock.patch('json.dumps', return_value='{}')
def test_print_information_no_plugins(dumps, information, print_mock):
    """Verify we print and exit only when we have plugins."""
    plugins = []
    option_manager = mock.Mock(registered_plugins=set(plugins))
    assert debug.print_information(
        None, None, None, None, option_manager=option_manager,
    ) is None
    assert dumps.called is False
    assert information.called is False
    assert print_mock.called is False


@mock.patch('flake8.main.debug.print')
@mock.patch('flake8.main.debug.information', return_value={})
@mock.patch('json.dumps', return_value='{}')
def test_print_information(dumps, information, print_mock):
    """Verify we print and exit only when we have plugins."""
    plugins = [
        manager.PluginVersion('pycodestyle', '2.0.0', False),
        manager.PluginVersion('mccabe', '0.5.9', False),
    ]
    option_manager = mock.Mock(registered_plugins=set(plugins))
    with pytest.raises(SystemExit):
        debug.print_information(
            None, None, None, None, option_manager=option_manager,
        )
    print_mock.assert_called_once_with('{}')
    dumps.assert_called_once_with({}, indent=2, sort_keys=True)
    information.assert_called_once_with(option_manager)
