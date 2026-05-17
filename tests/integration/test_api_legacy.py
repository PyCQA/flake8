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


def test_legacy_api_parallel_checks_use_option_overrides(tmpdir):
    long_line = f"x = \"{'a' * 80}\"\n"
    assert len(long_line.rstrip()) == 86

    file1 = tmpdir.join("file1.py")
    file1.write(long_line)
    file2 = tmpdir.join("file2.py")
    file2.write(long_line)

    style_guide = legacy.get_style_guide(max_line_length=88)
    report = style_guide.check_files([file1.strpath, file2.strpath])
    assert report.total_errors == 0
