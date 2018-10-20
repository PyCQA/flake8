"""Unit tests for flake.options.manager.OptionManager."""
import optparse
import os

import mock
import pytest

from flake8 import utils
from flake8.options import manager

TEST_VERSION = '3.0.0b1'


@pytest.fixture
def optmanager():
    """Generate a simple OptionManager with default test arguments."""
    return manager.OptionManager(prog='flake8', version=TEST_VERSION)


def test_option_manager_creates_option_parser(optmanager):
    """Verify that a new manager creates a new parser."""
    assert optmanager.parser is not None
    assert isinstance(optmanager.parser, optparse.OptionParser) is True


def test_add_option_short_option_only(optmanager):
    """Verify the behaviour of adding a short-option only."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('-s', help='Test short opt')
    assert optmanager.options[0].short_option_name == '-s'


def test_add_option_long_option_only(optmanager):
    """Verify the behaviour of adding a long-option only."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--long', help='Test long opt')
    assert optmanager.options[0].short_option_name is None
    assert optmanager.options[0].long_option_name == '--long'


def test_add_short_and_long_option_names(optmanager):
    """Verify the behaviour of using both short and long option names."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('-b', '--both', help='Test both opts')
    assert optmanager.options[0].short_option_name == '-b'
    assert optmanager.options[0].long_option_name == '--both'


def test_add_option_with_custom_args(optmanager):
    """Verify that add_option handles custom Flake8 parameters."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--parse', parse_from_config=True)
    optmanager.add_option('--commas', comma_separated_list=True)
    optmanager.add_option('--files', normalize_paths=True)

    attrs = ['parse_from_config', 'comma_separated_list', 'normalize_paths']
    for option, attr in zip(optmanager.options, attrs):
        assert getattr(option, attr) is True


def test_parse_args_normalize_path(optmanager):
    """Show that parse_args handles path normalization."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--config', normalize_paths=True)

    options, args = optmanager.parse_args(['--config', '../config.ini'])
    assert options.config == os.path.abspath('../config.ini')


def test_parse_args_handles_comma_separated_defaults(optmanager):
    """Show that parse_args handles defaults that are comma-separated."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--exclude', default='E123,W234',
                          comma_separated_list=True)

    options, args = optmanager.parse_args([])
    assert options.exclude == ['E123', 'W234']


def test_parse_args_handles_comma_separated_lists(optmanager):
    """Show that parse_args handles user-specified comma-separated lists."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--exclude', default='E123,W234',
                          comma_separated_list=True)

    options, args = optmanager.parse_args(['--exclude', 'E201,W111,F280'])
    assert options.exclude == ['E201', 'W111', 'F280']


def test_parse_args_normalize_paths(optmanager):
    """Verify parse_args normalizes a comma-separated list of paths."""
    assert optmanager.options == []
    assert optmanager.config_options_dict == {}

    optmanager.add_option('--extra-config', normalize_paths=True,
                          comma_separated_list=True)

    options, args = optmanager.parse_args([
        '--extra-config', '../config.ini,tox.ini,flake8/some-other.cfg'
    ])
    assert options.extra_config == [
        os.path.abspath('../config.ini'),
        'tox.ini',
        os.path.abspath('flake8/some-other.cfg'),
    ]


def test_format_plugin():
    """Verify that format_plugin turns a tuple into a dictionary."""
    plugin = manager.OptionManager.format_plugin(
        manager.PluginVersion('Testing', '0.0.0', False)
    )
    assert plugin['name'] == 'Testing'
    assert plugin['version'] == '0.0.0'


def test_generate_versions(optmanager):
    """Verify a comma-separated string is generated of registered plugins."""
    optmanager.registered_plugins = [
        manager.PluginVersion('Testing 100', '0.0.0', False),
        manager.PluginVersion('Testing 101', '0.0.0', False),
        manager.PluginVersion('Testing 300', '0.0.0', True),
    ]
    assert (optmanager.generate_versions()
            == 'Testing 100: 0.0.0, Testing 101: 0.0.0, Testing 300: 0.0.0')


def test_plugins_are_sorted_in_generate_versions(optmanager):
    """Verify we sort before joining strings in generate_versions."""
    optmanager.registered_plugins = [
        manager.PluginVersion('pyflakes', '1.5.0', False),
        manager.PluginVersion('mccabe', '0.7.0', False),
        manager.PluginVersion('pycodestyle', '2.2.0', False),
        manager.PluginVersion('flake8-docstrings', '0.6.1', False),
        manager.PluginVersion('flake8-bugbear', '2016.12.1', False),
    ]
    assert (optmanager.generate_versions()
            == 'flake8-bugbear: 2016.12.1, '
               'flake8-docstrings: 0.6.1, '
               'mccabe: 0.7.0, '
               'pycodestyle: 2.2.0, '
               'pyflakes: 1.5.0')


def test_generate_versions_with_format_string(optmanager):
    """Verify a comma-separated string is generated of registered plugins."""
    optmanager.registered_plugins.update([
        manager.PluginVersion('Testing', '0.0.0', False),
        manager.PluginVersion('Testing', '0.0.0', False),
        manager.PluginVersion('Testing', '0.0.0', False),
    ])
    assert (
        optmanager.generate_versions() == 'Testing: 0.0.0'
    )


def test_update_version_string(optmanager):
    """Verify we update the version string idempotently."""
    assert optmanager.version == TEST_VERSION
    assert optmanager.parser.version == TEST_VERSION

    optmanager.registered_plugins = [
        manager.PluginVersion('Testing 100', '0.0.0', False),
        manager.PluginVersion('Testing 101', '0.0.0', False),
        manager.PluginVersion('Testing 300', '0.0.0', False),
    ]

    optmanager.update_version_string()

    assert optmanager.version == TEST_VERSION
    assert (optmanager.parser.version == TEST_VERSION
            + ' (Testing 100: 0.0.0, Testing 101: 0.0.0, Testing 300: 0.0.0) '
            + utils.get_python_version())


def test_generate_epilog(optmanager):
    """Verify how we generate the epilog for help text."""
    assert optmanager.parser.epilog is None

    optmanager.registered_plugins = [
        manager.PluginVersion('Testing 100', '0.0.0', False),
        manager.PluginVersion('Testing 101', '0.0.0', False),
        manager.PluginVersion('Testing 300', '0.0.0', False),
    ]

    expected_value = (
        'Installed plugins: Testing 100: 0.0.0, Testing 101: 0.0.0, Testing'
        ' 300: 0.0.0'
    )

    optmanager.generate_epilog()
    assert optmanager.parser.epilog == expected_value


def test_extend_default_ignore(optmanager):
    """Verify that we update the extended default ignore list."""
    assert optmanager.extended_default_ignore == set()

    optmanager.extend_default_ignore(['T100', 'T101', 'T102'])
    assert optmanager.extended_default_ignore == {'T100',
                                                  'T101',
                                                  'T102'}


def test_parse_known_args(optmanager):
    """Verify we ignore unknown options."""
    with mock.patch('sys.exit') as sysexit:
        optmanager.parse_known_args(['--max-complexity', '5'])

    assert sysexit.called is False
