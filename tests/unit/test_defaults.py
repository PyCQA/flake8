from __future__ import annotations

import pytest

from flake8.defaults import VALID_CODE_PREFIX


@pytest.mark.parametrize(
    "s",
    (
        "E",
        "E1",
        "E123",
        "ABC",
        "ABC1",
        "ABC123",
    ),
)
def test_valid_plugin_prefixes(s):
    assert VALID_CODE_PREFIX.match(s)


@pytest.mark.parametrize(
    "s",
    (
        "",
        "A1234",
        "ABCD",
        "abc",
        "a-b",
        "☃",
        "A𝟗",
    ),
)
def test_invalid_plugin_prefixes(s):
    assert VALID_CODE_PREFIX.match(s) is None
