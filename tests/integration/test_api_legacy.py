"""Integration tests for the legacy api."""
from __future__ import annotations

from flake8.api import legacy


def test_legacy_api(tmpdir):
    """A basic end-to-end test for the legacy api reporting errors."""
    with tmpdir.as_cwd():
        t_py = tmpdir.join("t.py")
        t_py.write("import os  # unused import\n")

        style_guide = legacy.get_style_guide()
        report = style_guide.check_files([t_py.strpath])
        assert report.total_errors == 1
