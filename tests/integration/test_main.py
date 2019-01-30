"""Integration tests for the main entrypoint of flake8."""
import mock

from flake8 import utils
from flake8.main import application


def test_diff_option(tmpdir, capsys):
    """Ensure that `flake8 --diff` works."""
    t_py_contents = '''\
import os
import sys  # unused but not part of diff

print('(to avoid trailing whitespace in test)')
print('(to avoid trailing whitespace in test)')
print(os.path.join('foo', 'bar'))

y  # part of the diff and an error
'''

    diff = '''\
diff --git a/t.py b/t.py
index d64ac39..7d943de 100644
--- a/t.py
+++ b/t.py
@@ -4,3 +4,5 @@ import sys  # unused but not part of diff
 print('(to avoid trailing whitespace in test)')
 print('(to avoid trailing whitespace in test)')
 print(os.path.join('foo', 'bar'))
+
+y  # part of the diff and an error
'''

    with mock.patch.object(utils, 'stdin_get_value', return_value=diff):
        with tmpdir.as_cwd():
            tmpdir.join('t.py').write(t_py_contents)

            app = application.Application()
            app.run(['--diff'])

    out, err = capsys.readouterr()
    assert out == "t.py:8:1: F821 undefined name 'y'\n"
    assert err == ''


def test_statistics_option(tmpdir, capsys):
    """Ensure that `flake8 --statistics` works."""
    with tmpdir.as_cwd():
        tmpdir.join('t.py').write('import os\nimport sys\n')

        app = application.Application()
        app.run(['--statistics', 't.py'])

    out, err = capsys.readouterr()
    assert out == '''\
t.py:1:1: F401 'os' imported but unused
t.py:2:1: F401 'sys' imported but unused
2     F401 'os' imported but unused
'''
    assert err == ''
