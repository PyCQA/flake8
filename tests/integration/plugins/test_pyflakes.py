from __future__ import annotations

from flake8.main.cli import main


def test_pyflakes_builtins(tmpdir, capsys):
    t_py = tmpdir.join('t.py')
    t_py.write('print(b)\n')

    expected = "t.py:1:7: F821 undefined name 'b'\n"
    with tmpdir.as_cwd():
        ret = main(('t.py',))
    out, err = capsys.readouterr()
    assert (ret, out, err) == (1, expected, '')

    with tmpdir.as_cwd():
        ret = main(('t.py', '--builtins', 'b'))
    out, err = capsys.readouterr()
    assert (ret, out, err) == (0, '', '')
