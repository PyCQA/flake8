=================
 Testing plugins
=================

This section describes practical ways to verify that a |Flake8| plugin behaves
the way you expect. It complements :ref:`register-a-plugin`, which explains
how to expose your code to |Flake8| via entry points.

Install the package you are testing (for example with ``pip install -e .`` in
your project root) so metadata and entry points are visible to |Flake8| in the
same environment that runs your tests.

.. note::

   The programmatic API lives in :mod:`flake8.api.legacy`. For background and
   full reference, see :doc:`../user/python-api`.

   :meth:`~flake8.api.legacy.StyleGuide.input_file` **does not** accept in-memory
   ``lines`` anymore: since |Flake8| 3.0 those arguments are ignored, and only
   the path is checked. For tests, write source to a temporary file and pass
   that path to :meth:`~flake8.api.legacy.StyleGuide.check_files`.

Programmatic checks
===================

Use :func:`~flake8.api.legacy.get_style_guide` to build a
:class:`~flake8.api.legacy.StyleGuide`, then call
:meth:`~flake8.api.legacy.StyleGuide.check_files` with a list of paths. The
returned :class:`~flake8.api.legacy.Report` exposes
:attr:`~flake8.api.legacy.Report.total_errors` and
:meth:`~flake8.api.legacy.Report.get_statistics`.

Limit reported codes to those from your plugin (prefix matching works the same
as for ``--select`` on the command line) so unrelated built-in violations do not
make assertions brittle:

.. code-block:: python

    from pathlib import Path

    from flake8.api import legacy


    def test_plugin_reports_violation(tmp_path):
        example = tmp_path / "example.py"
        example.write_text("# plugin-specific bad pattern\n", encoding="utf-8")

        style_guide = legacy.get_style_guide(select=["X"])
        report = style_guide.check_files([str(example)])

        assert report.total_errors == 1

Run the full default |Flake8| selection when you want an integration-style test
that your plugin plays nicely with everything else a user would run:

.. code-block:: python

    style_guide = legacy.get_style_guide()
    report = style_guide.check_files([str(example)])

Keyword arguments to :func:`~flake8.api.legacy.get_style_guide` correspond to
parsed command-line options on the application (for example ``select``,
``ignore``, ``exclude``). Only attributes that already exist on the options
object can be set; unknown names are logged and ignored.

Command-line checks
===================

End-to-end tests can invoke the same entry point users run:

.. code-block:: python

    import subprocess
    import sys


    def test_flake8_cli(tmp_path):
        target = tmp_path / "example.py"
        target.write_text("...\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "flake8", "--select=X", str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "X" in result.stdout

Use ``--select`` (or ``--extend-select``) to focus on your plugin's codes when
asserting on output text.
