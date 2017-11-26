"""Module containing tests for the setuptools command integration."""
import pytest
from setuptools import dist

from flake8.main import setuptools_command


@pytest.fixture
def distribution():
    """Create a setuptools Distribution object."""
    return dist.Distribution({
        'name': 'foo',
        'packages': [
            'foo',
            'foo.bar',
            'foo_biz',
        ],
    })


@pytest.fixture
def command(distribution):
    """Create an instance of Flake8's setuptools command."""
    return setuptools_command.Flake8(distribution)


def test_package_files_removes_submodules(command):
    """Verify that we collect all package files."""
    package_files = list(command.package_files())
    assert sorted(package_files) == [
        'foo',
        'foo_biz',
    ]
