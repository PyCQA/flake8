"""Unit tests for flake.options.manager.OptionManager."""
import argparse
import os

import mock
import pytest

from flake8 import utils
from flake8.main.options import JobsArgument
from flake8.options import manager

TEST_VERSION = '3.0.0b1'


@pytest.fixture
def optmanager():
    """Generate a simple OptionManager with default test arguments."""
    return manager.OptionManager(prog='flake8', version=TEST_VERSION)


def test_option_manager_creates_option_parser(optmanager):
    """Verify that a new manager creates a new parser."""
    assert isinstance(optmanager.parser, argparse.ArgumentParser)


def test_option_manager_including_parent_options():
    """Verify parent options are included in the parsed options."""
    # GIVEN
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--parent')

    # WHEN
    optmanager = manager.OptionManager(
        prog='flake8',
        version=TEST_VERSION,
        parents=[parent_parser])
    option, _ = optmanager.parse_args(['--parent', 'foo'])

    # THEN
    assert option.parent == 'foo'


def test_parse_args_forwarding_default_values(optmanager):
    """Verify default provided values are present in the final result."""
    namespace = argparse.Namespace(foo='bar')
    options, args = optmanager.parse_args([], namespace)
    assert options.foo == 'bar'


def test_parse_args_forwarding_type_coercion(optmanager):
    """Verify default provided values are type converted from add_option."""
    optmanager.add_option('--foo', type=int)
    namespace = argparse.Namespace(foo='5')
    options, args = optmanager.parse_args([], namespace)
    assert options.foo == 5


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
    assert optmanager.options[0].short_option_name is manager._ARG.NO
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
    assert optmanager.version_action.version == TEST_VERSION

    optmanager.registered_plugins = [
        manager.PluginVersion('Testing 100', '0.0.0', False),
        manager.PluginVersion('Testing 101', '0.0.0', False),
        manager.PluginVersion('Testing 300', '0.0.0', False),
    ]

    optmanager.update_version_string()

    assert optmanager.version == TEST_VERSION
    assert (optmanager.version_action.version == TEST_VERSION
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
    assert optmanager.extended_default_ignore == {'T100', 'T101', 'T102'}


def test_parse_known_args(optmanager):
    """Verify we ignore unknown options."""
    with mock.patch('sys.exit') as sysexit:
        optmanager.parse_known_args(['--max-complexity', '5'])

    assert sysexit.called is False


def test_optparse_normalize_callback_option_legacy(optmanager):
    """Test the optparse shim for `callback=`."""
    callback_foo = mock.Mock()
    optmanager.add_option(
        '--foo',
        action='callback',
        callback=callback_foo,
        callback_args=(1, 2),
        callback_kwargs={'a': 'b'},
    )
    callback_bar = mock.Mock()
    optmanager.add_option(
        '--bar',
        action='callback',
        type='string',
        callback=callback_bar,
    )
    callback_baz = mock.Mock()
    optmanager.add_option(
        '--baz',
        action='callback',
        type='string',
        nargs=2,
        callback=callback_baz,
    )

    optmanager.parse_args(['--foo', '--bar', 'bararg', '--baz', '1', '2'])

    callback_foo.assert_called_once_with(
        mock.ANY,  # the option / action instance
        '--foo',
        None,
        mock.ANY,  # the OptionParser / ArgumentParser
        1,
        2,
        a='b',
    )
    callback_bar.assert_called_once_with(
        mock.ANY,  # the option / action instance
        '--bar',
        'bararg',
        mock.ANY,  # the OptionParser / ArgumentParser
    )
    callback_baz.assert_called_once_with(
        mock.ANY,  # the option / action instance
        '--baz',
        ('1', '2'),
        mock.ANY,  # the OptionParser / ArgumentParser
    )


@pytest.mark.parametrize(
    ('type_s', 'input_val', 'expected'),
    (
        ('int', '5', 5),
        ('long', '6', 6),
        ('string', 'foo', 'foo'),
        ('float', '1.5', 1.5),
        ('complex', '1+5j', 1 + 5j),
        # optparse allows this but does not document it
        ('str', 'foo', 'foo'),
    ),
)
def test_optparse_normalize_types(optmanager, type_s, input_val, expected):
    """Test the optparse shim for type="typename"."""
    optmanager.add_option('--foo', type=type_s)
    opts, args = optmanager.parse_args(['--foo', input_val])
    assert opts.foo == expected


def test_optparse_normalize_choice_type(optmanager):
    """Test the optparse shim for type="choice"."""
    optmanager.add_option('--foo', type='choice', choices=('1', '2', '3'))
    opts, args = optmanager.parse_args(['--foo', '1'])
    assert opts.foo == '1'
    # fails to parse
    with pytest.raises(SystemExit):
        optmanager.parse_args(['--foo', '4'])


def test_optparse_normalize_help(optmanager, capsys):
    """Test the optparse shim for %default in help text."""
    optmanager.add_option('--foo', default='bar', help='default: %default')
    with pytest.raises(SystemExit):
        optmanager.parse_args(['--help'])
    out, err = capsys.readouterr()
    output = out + err
    assert 'default: bar' in output


def test_optmanager_group(optmanager, capsys):
    """Test that group(...) causes options to be assigned to a group."""
    with optmanager.group('groupname'):
        optmanager.add_option('--foo')
    with pytest.raises(SystemExit):
        optmanager.parse_args(['--help'])
    out, err = capsys.readouterr()
    output = out + err
    assert '\ngroupname:\n' in output


@pytest.mark.parametrize(
    ("s", "is_auto", "n_jobs"),
    (
        ("auto", True, -1),
        ("4", False, 4),
    ),
)
def test_parse_valid_jobs_argument(s, is_auto, n_jobs):
    """Test that --jobs properly parses valid arguments."""
    jobs_opt = JobsArgument(s)
    assert is_auto == jobs_opt.is_auto
    assert n_jobs == jobs_opt.n_jobs


def test_parse_invalid_jobs_argument(optmanager, capsys):
    """Test that --jobs properly rejects invalid arguments."""
    namespace = argparse.Namespace()
    optmanager.add_option("--jobs", type=JobsArgument)
    with pytest.raises(SystemExit):
        optmanager.parse_args(["--jobs=foo"], namespace)
    out, err = capsys.readouterr()
    output = out + err
    expected = (
        "\nflake8: error: argument --jobs: "
        "'foo' must be 'auto' or an integer.\n"
    )
    assert expected in output


def test_jobs_argument_str():
    """Test that JobsArgument has a correct __str__."""
    assert str(JobsArgument("auto")) == "auto"
    assert str(JobsArgument("123")) == "123"
