"""Unit tests for flake8.options.manager.Option."""
import mock
import pytest

from flake8.options import manager


def test_to_optparse():
    """Test conversion to an optparse.Option class."""
    opt = manager.Option(
        short_option_name='-t',
        long_option_name='--test',
        action='count',
        parse_from_config=True,
        normalize_paths=True,
    )
    assert opt.normalize_paths is True
    assert opt.parse_from_config is True

    optparse_opt = opt.to_optparse()
    assert not hasattr(optparse_opt, 'parse_from_config')
    assert not hasattr(optparse_opt, 'normalize_paths')
    assert optparse_opt.action == 'count'


@pytest.mark.parametrize('opttype,str_val,expected', [
    ('float', '2', 2.0),
    ('complex', '2', (2 + 0j)),
])
def test_to_support_optparses_standard_types(opttype, str_val, expected):
    """Show that optparse converts float and complex types correctly."""
    opt = manager.Option('-t', '--test', type=opttype)
    assert opt.normalize_from_setuptools(str_val) == expected


@mock.patch('optparse.Option')
def test_to_optparse_creates_an_option_as_we_expect(Option):  # noqa: N803
    """Show that we pass all keyword args to optparse.Option."""
    opt = manager.Option('-t', '--test', action='count')
    opt.to_optparse()
    option_kwargs = {
        'action': 'count',
        'default': None,
        'type': None,
        'dest': 'test',
        'nargs': None,
        'const': None,
        'choices': None,
        'callback': None,
        'callback_args': None,
        'callback_kwargs': None,
        'help': None,
        'metavar': None,
    }

    Option.assert_called_once_with(
        '-t', '--test', **option_kwargs
    )


def test_config_name_generation():
    """Show that we generate the config name deterministically."""
    opt = manager.Option(long_option_name='--some-very-long-option-name',
                         parse_from_config=True)

    assert opt.config_name == 'some_very_long_option_name'


def test_config_name_needs_long_option_name():
    """Show that we error out if the Option should be parsed from config."""
    with pytest.raises(ValueError):
        manager.Option('-s', parse_from_config=True)


def test_dest_is_not_overridden():
    """Show that we do not override custom destinations."""
    opt = manager.Option('-s', '--short', dest='something_not_short')
    assert opt.dest == 'something_not_short'
