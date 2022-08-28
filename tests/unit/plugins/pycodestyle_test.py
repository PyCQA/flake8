from __future__ import annotations

import importlib.machinery
import importlib.util
import os.path

import flake8.plugins.pycodestyle

HERE = os.path.dirname(os.path.abspath(__file__))


def test_up_to_date():
    """Validate that the generated pycodestyle plugin is up to date.

    We generate two "meta" plugins for pycodestyle to avoid calling overhead.

    To regenerate run:

        ./bin/gen-pycodestyle-plugin > src/flake8/plugins/pycodestyle.py
    """

    path = os.path.join(HERE, "../../../bin/gen-pycodestyle-plugin")
    name = os.path.basename(path)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)

    expected = "".join(f"{line}\n" for line in mod.lines())

    with open(flake8.plugins.pycodestyle.__file__) as f:
        contents = f.read()

    assert contents == expected
