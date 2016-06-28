"""Tests for flake8's utils module."""
import os

import mock
import pytest

from flake8 import utils
from flake8.plugins import manager as plugin_manager

RELATIVE_PATHS = ["flake8", "pep8", "pyflakes", "mccabe"]


@pytest.mark.parametrize("value,expected", [
    ("E123,\n\tW234,\n    E206", ["E123", "W234", "E206"]),
    ("E123,W234,E206", ["E123", "W234", "E206"]),
    (["E123", "W234", "E206"], ["E123", "W234", "E206"]),
    (["E123", "\n\tW234", "\n    E206"], ["E123", "W234", "E206"]),
])
def test_parse_comma_separated_list(value, expected):
    """Verify that similar inputs produce identical outputs."""
    assert utils.parse_comma_separated_list(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("flake8", "flake8"),
    ("../flake8", os.path.abspath("../flake8")),
    ("flake8/", os.path.abspath("flake8")),
])
def test_normalize_path(value, expected):
    """Verify that we normalize paths provided to the tool."""
    assert utils.normalize_path(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("flake8,pep8,pyflakes,mccabe", ["flake8", "pep8", "pyflakes", "mccabe"]),
    ("flake8,\n\tpep8,\n  pyflakes,\n\n    mccabe",
        ["flake8", "pep8", "pyflakes", "mccabe"]),
    ("../flake8,../pep8,../pyflakes,../mccabe",
        [os.path.abspath("../" + p) for p in RELATIVE_PATHS]),
])
def test_normalize_paths(value, expected):
    """Verify we normalize comma-separated paths provided to the tool."""
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


def test_fnmatch_returns_the_default_with_empty_default():
    """The default parameter should be returned when no patterns are given."""
    sentinel = object()
    assert utils.fnmatch('file.py', [], default=sentinel) is sentinel


def test_filenames_from_a_directory():
    """Verify that filenames_from walks a directory."""
    filenames = list(utils.filenames_from('src/flake8/'))
    assert len(filenames) > 2
    assert 'src/flake8/__init__.py' in filenames


def test_filenames_from_a_directory_with_a_predicate():
    """Verify that predicates filter filenames_from."""
    filenames = list(utils.filenames_from(
        arg='src/flake8/',
        predicate=lambda filename: filename == 'flake8/__init__.py',
    ))
    assert len(filenames) > 2
    assert 'flake8/__init__.py' not in filenames


def test_filenames_from_a_single_file():
    """Verify that we simply yield that filename."""
    filenames = list(utils.filenames_from('flake8/__init__.py'))

    assert len(filenames) == 1
    assert ['flake8/__init__.py'] == filenames


def test_parameters_for_class_plugin():
    """Verify that we can retrieve the parameters for a class plugin."""
    class FakeCheck(object):
        def __init__(self, tree):
            pass

    plugin = plugin_manager.Plugin('plugin-name', object())
    plugin._plugin = FakeCheck
    assert utils.parameters_for(plugin) == {'tree': True}


def test_parameters_for_function_plugin():
    """Verify that we retrieve the parameters for a function plugin."""
    def fake_plugin(physical_line, self, tree, optional=None):
        pass

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
