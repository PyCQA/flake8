"""Tests for flake8's utils module."""
import io
import logging
import os
import sys

import mock
import pytest

from flake8 import exceptions
from flake8 import utils
from flake8.plugins import manager as plugin_manager

RELATIVE_PATHS = ["flake8", "pep8", "pyflakes", "mccabe"]


@pytest.mark.parametrize("value,expected", [
    ("E123,\n\tW234,\n    E206", ["E123", "W234", "E206"]),
    ("E123,W234,E206", ["E123", "W234", "E206"]),
    ("E123 W234 E206", ["E123", "W234", "E206"]),
    ("E123\nW234 E206", ["E123", "W234", "E206"]),
    ("E123\nW234\nE206", ["E123", "W234", "E206"]),
    ("E123,W234,E206,", ["E123", "W234", "E206"]),
    ("E123,W234,E206, ,\n", ["E123", "W234", "E206"]),
    ("E123,W234,,E206,,", ["E123", "W234", "E206"]),
    ("E123, W234,, E206,,", ["E123", "W234", "E206"]),
    ("E123,,W234,,E206,,", ["E123", "W234", "E206"]),
    ("", []),
])
def test_parse_comma_separated_list(value, expected):
    """Verify that similar inputs produce identical outputs."""
    assert utils.parse_comma_separated_list(value) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    (
        # empty option configures nothing
        ('', []), ('   ', []), ('\n\n\n', []),
        # basic case
        (
            'f.py:E123',
            [('f.py', ['E123'])],
        ),
        # multiple filenames, multiple codes
        (
            'f.py,g.py:E,F',
            [('f.py', ['E', 'F']), ('g.py', ['E', 'F'])],
        ),
        # demonstrate that whitespace is not important around tokens
        (
            '   f.py  , g.py  : E  , F  ',
            [('f.py', ['E', 'F']), ('g.py', ['E', 'F'])],
        ),
        # whitespace can separate groups of configuration
        (
            'f.py:E g.py:F',
            [('f.py', ['E']), ('g.py', ['F'])],
        ),
        # newlines can separate groups of configuration
        (
            'f.py: E\ng.py: F\n',
            [('f.py', ['E']), ('g.py', ['F'])],
        ),
        # whitespace can be used in place of commas
        (
            'f.py g.py: E F',
            [('f.py', ['E', 'F']), ('g.py', ['E', 'F'])],
        ),
        # go ahead, indent your codes
        (
            'f.py:\n    E,F\ng.py:\n    G,H',
            [('f.py', ['E', 'F']), ('g.py', ['G', 'H'])],
        ),
        # capitalized filenames are ok too
        (
            'F.py,G.py: F,G',
            [('F.py', ['F', 'G']), ('G.py', ['F', 'G'])],
        ),
        #  it's easier to allow zero filenames or zero codes than forbid it
        (':E', []), ('f.py:', []),
        (':E f.py:F', [('f.py', ['F'])]),
        ('f.py: g.py:F', [('g.py', ['F'])]),
        ('f.py:E:', []),
        ('f.py:E.py:', []),
        ('f.py:Eg.py:F', [('Eg.py', ['F'])]),
        # sequences are also valid (?)
        (
            ['f.py:E,F', 'g.py:G,H'],
            [('f.py', ['E', 'F']), ('g.py', ['G', 'H'])],
        ),
        # six-digits codes are allowed
        (
            'f.py: ABC123',
            [('f.py', ['ABC123'])],
        )
    ),
)
def test_parse_files_to_codes_mapping(value, expected):
    """Test parsing of valid files-to-codes mappings."""
    assert utils.parse_files_to_codes_mapping(value) == expected


@pytest.mark.parametrize(
    'value',
    (
        # code while looking for filenames
        'E123', 'f.py,E123', 'f.py E123',
        # eof while looking for filenames
        'f.py', 'f.py:E,g.py'
        # colon while looking for codes
        'f.py::',
        # no separator between
        'f.py:E1F1',
    ),
)
def test_invalid_file_list(value):
    """Test parsing of invalid files-to-codes mappings."""
    with pytest.raises(exceptions.ExecutionError):
        utils.parse_files_to_codes_mapping(value)


@pytest.mark.parametrize("value,expected", [
    ("flake8", "flake8"),
    ("../flake8", os.path.abspath("../flake8")),
    ("flake8/", os.path.abspath("flake8")),
])
def test_normalize_path(value, expected):
    """Verify that we normalize paths provided to the tool."""
    assert utils.normalize_path(value) == expected


@pytest.mark.parametrize("value,expected", [
    (["flake8", "pep8", "pyflakes", "mccabe"],
        ["flake8", "pep8", "pyflakes", "mccabe"]),
    (["../flake8", "../pep8", "../pyflakes", "../mccabe"],
        [os.path.abspath("../" + p) for p in RELATIVE_PATHS]),
])
def test_normalize_paths(value, expected):
    """Verify we normalizes a sequence of paths provided to the tool."""
    assert utils.normalize_paths(value) == expected


def test_is_windows_checks_for_nt():
    """Verify that we correctly detect Windows."""
    with mock.patch.object(os, 'name', 'nt'):
        assert utils.is_windows() is True

    with mock.patch.object(os, 'name', 'posix'):
        assert utils.is_windows() is False


@pytest.mark.parametrize('filename,patterns,expected', [
    ('foo.py', [], True),
    ('foo.py', ['*.pyc'], False),
    ('foo.pyc', ['*.pyc'], True),
    ('foo.pyc', ['*.swp', '*.pyc', '*.py'], True),
])
def test_fnmatch(filename, patterns, expected):
    """Verify that our fnmatch wrapper works as expected."""
    assert utils.fnmatch(filename, patterns) is expected


@pytest.fixture
def files_dir(tmpdir):
    """Create test dir for testing filenames_from."""
    with tmpdir.as_cwd():
        tmpdir.join('a/b/c.py').ensure()
        tmpdir.join('a/b/d.py').ensure()
        tmpdir.join('a/b/e/f.py').ensure()
        yield tmpdir


def _normpath(s):
    return s.replace('/', os.sep)


def _normpaths(pths):
    return {_normpath(pth) for pth in pths}


@pytest.mark.usefixtures('files_dir')
def test_filenames_from_a_directory():
    """Verify that filenames_from walks a directory."""
    filenames = set(utils.filenames_from(_normpath('a/b/')))
    # should include all files
    expected = _normpaths(('a/b/c.py', 'a/b/d.py', 'a/b/e/f.py'))
    assert filenames == expected


@pytest.mark.usefixtures('files_dir')
def test_filenames_from_a_directory_with_a_predicate():
    """Verify that predicates filter filenames_from."""
    filenames = set(utils.filenames_from(
        arg=_normpath('a/b/'),
        predicate=lambda path: path.endswith(_normpath('b/c.py')),
    ))
    # should not include c.py
    expected = _normpaths(('a/b/d.py', 'a/b/e/f.py'))
    assert filenames == expected


@pytest.mark.usefixtures('files_dir')
def test_filenames_from_a_directory_with_a_predicate_from_the_current_dir():
    """Verify that predicates filter filenames_from."""
    filenames = set(utils.filenames_from(
        arg=_normpath('./a/b'),
        predicate=lambda path: path == 'c.py',
    ))
    # none should have matched the predicate so all returned
    expected = _normpaths(('./a/b/c.py', './a/b/d.py', './a/b/e/f.py'))
    assert filenames == expected


@pytest.mark.usefixtures('files_dir')
def test_filenames_from_a_single_file():
    """Verify that we simply yield that filename."""
    filenames = set(utils.filenames_from(_normpath('a/b/c.py')))
    assert filenames == {_normpath('a/b/c.py')}


def test_filenames_from_a_single_file_does_not_exist():
    """Verify that a passed filename which does not exist is returned back."""
    filenames = set(utils.filenames_from(_normpath('d/n/e.py')))
    assert filenames == {_normpath('d/n/e.py')}


def test_filenames_from_exclude_doesnt_exclude_directory_names(tmpdir):
    """Verify that we don't greedily exclude subdirs."""
    tmpdir.join('1').ensure_dir().join('dont_return_me.py').ensure()
    tmpdir.join('2').join('1').ensure_dir().join('return_me.py').ensure()
    exclude = [tmpdir.join('1').strpath]

    # This acts similar to src.flake8.checker.is_path_excluded
    def predicate(pth):
        return utils.fnmatch(os.path.abspath(pth), exclude)

    with tmpdir.as_cwd():
        filenames = list(utils.filenames_from('.', predicate))
    assert filenames == [os.path.join('.', '2', '1', 'return_me.py')]


def test_parameters_for_class_plugin():
    """Verify that we can retrieve the parameters for a class plugin."""
    class FakeCheck(object):
        def __init__(self, tree):
            raise NotImplementedError

    plugin = plugin_manager.Plugin('plugin-name', object())
    plugin._plugin = FakeCheck
    assert utils.parameters_for(plugin) == {'tree': True}


def test_parameters_for_function_plugin():
    """Verify that we retrieve the parameters for a function plugin."""
    def fake_plugin(physical_line, self, tree, optional=None):
        raise NotImplementedError

    plugin = plugin_manager.Plugin('plugin-name', object())
    plugin._plugin = fake_plugin
    assert utils.parameters_for(plugin) == {
        'physical_line': True,
        'self': True,
        'tree': True,
        'optional': False,
    }


def read_diff_file(filename):
    """Read the diff file in its entirety."""
    with open(filename, 'r') as fd:
        content = fd.read()
    return content


SINGLE_FILE_DIFF = read_diff_file('tests/fixtures/diffs/single_file_diff')
SINGLE_FILE_INFO = {
    'flake8/utils.py': set(range(75, 83)).union(set(range(84, 94))),
}
TWO_FILE_DIFF = read_diff_file('tests/fixtures/diffs/two_file_diff')
TWO_FILE_INFO = {
    'flake8/utils.py': set(range(75, 83)).union(set(range(84, 94))),
    'tests/unit/test_utils.py': set(range(115, 128)),
}
MULTI_FILE_DIFF = read_diff_file('tests/fixtures/diffs/multi_file_diff')
MULTI_FILE_INFO = {
    'flake8/utils.py': set(range(75, 83)).union(set(range(84, 94))),
    'tests/unit/test_utils.py': set(range(115, 129)),
    'tests/fixtures/diffs/single_file_diff': set(range(1, 28)),
    'tests/fixtures/diffs/two_file_diff': set(range(1, 46)),
}


@pytest.mark.parametrize("diff, parsed_diff", [
    (SINGLE_FILE_DIFF, SINGLE_FILE_INFO),
    (TWO_FILE_DIFF, TWO_FILE_INFO),
    (MULTI_FILE_DIFF, MULTI_FILE_INFO),
])
def test_parse_unified_diff(diff, parsed_diff):
    """Verify that what we parse from a diff matches expectations."""
    assert utils.parse_unified_diff(diff) == parsed_diff


def test_matches_filename_for_excluding_dotfiles():
    """Verify that `.` and `..` are not matched by `.*`."""
    logger = logging.Logger(__name__)
    assert not utils.matches_filename('.', ('.*',), '', logger)
    assert not utils.matches_filename('..', ('.*',), '', logger)


@pytest.mark.xfail(sys.version_info < (3,), reason='py3+ only behaviour')
def test_stdin_get_value_crlf():
    """Ensure that stdin is normalized from crlf to lf."""
    stdin = io.TextIOWrapper(io.BytesIO(b'1\r\n2\r\n'), 'UTF-8')
    with mock.patch.object(sys, 'stdin', stdin):
        assert utils.stdin_get_value.__wrapped__() == '1\n2\n'
