"""Tests for flake8's utils module."""
import os

import pytest

from flake8 import utils


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
