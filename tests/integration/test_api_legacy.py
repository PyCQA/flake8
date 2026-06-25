"""Integration tests for the legacy api."""
from __future__ import annotations

from flake8.api import legacy
from flake8.main.options import JobsArgument


def test_legacy_api(tmpdir):
    """A basic end-to-end test for the legacy api reporting errors."""
    with tmpdir.as_cwd():
        t_py = tmpdir.join("t.py")
        t_py.write("import os  # unused import\n")

        style_guide = legacy.get_style_guide()
        report = style_guide.check_files([t_py.strpath])
        assert report.total_errors == 1


def test_legacy_api_uses_initialized_options_for_parallel_checks(tmpdir):
    with tmpdir.as_cwd():
        a_py = tmpdir.join("a.py")
        b_py = tmpdir.join("b.py")
        a_py.write('x = "' + "a" * 80 + '"\n')
        b_py.write('y = "' + "b" * 80 + '"\n')

        style_guide = legacy.get_style_guide(color="never", max_line_length=88)
        style_guide.options.jobs = JobsArgument("2")
        report = style_guide.check_files([a_py.strpath, b_py.strpath])

        assert report.total_errors == 0
