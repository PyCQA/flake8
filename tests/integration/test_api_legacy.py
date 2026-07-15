"""Integration tests for the legacy api."""
from __future__ import annotations

import subprocess
import sys
import textwrap

from flake8.api import legacy


def test_legacy_api(tmpdir):
    """A basic end-to-end test for the legacy api reporting errors."""
    with tmpdir.as_cwd():
        t_py = tmpdir.join("t.py")
        t_py.write("import os  # unused import\n")

        style_guide = legacy.get_style_guide()
        report = style_guide.check_files([t_py.strpath])
        assert report.total_errors == 1


def test_legacy_api_parallel_preserves_options(tmpdir):
    script = tmpdir.join("check.py")
    script.write(
        textwrap.dedent(
            """\
            import multiprocessing
            import tempfile
            from pathlib import Path

            from flake8.api import legacy


            if __name__ == "__main__":
                multiprocessing.set_start_method("spawn")
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    line = "x = " + repr("a" * 79) + "\\n"
                    paths = []
                    for name in ("one.py", "two.py"):
                        path = root / name
                        path.write_text(line)
                        paths.append(str(path))

                    style_guide = legacy.get_style_guide(
                        color="never", max_line_length=88,
                    )
                    report = style_guide.check_files(paths)
                    assert report.total_errors == 0
            """,
        ),
    )

    subprocess.run([sys.executable, script.strpath], check=True)
