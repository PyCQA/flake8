"""Integration tests for the main entrypoint of flake8."""
import json
import os

import mock
import pytest

from flake8 import utils
from flake8.main import cli


def _call_main(argv, retv=0):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(argv)
    assert excinfo.value.code == retv


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
            _call_main(['--diff'], retv=1)

    out, err = capsys.readouterr()
    assert out == "t.py:8:1: F821 undefined name 'y'\n"
    assert err == ''


def test_form_feed_line_split(tmpdir, capsys):
    """Test that form feed is treated the same for stdin."""
    src = 'x=1\n\f\ny=1\n'
    expected_out = '''\
t.py:1:2: E225 missing whitespace around operator
t.py:3:2: E225 missing whitespace around operator
'''

    with tmpdir.as_cwd():
        tmpdir.join('t.py').write(src)

        with mock.patch.object(utils, 'stdin_get_value', return_value=src):
            _call_main(['-', '--stdin-display-name=t.py'], retv=1)
            out, err = capsys.readouterr()
            assert out == expected_out
            assert err == ''

        _call_main(['t.py'], retv=1)
        out, err = capsys.readouterr()
        assert out == expected_out
        assert err == ''


def test_e101_indent_char_does_not_reset(tmpdir, capsys):
    """Ensure that E101 with an existing indent_char does not reset it."""
    t_py_contents = """\
if True:
    print('space indented')

s = '''\
\ttab indented
'''  # noqa: E101

if True:
    print('space indented')
"""

    with tmpdir.as_cwd():
        tmpdir.join('t.py').write(t_py_contents)
        _call_main(['t.py'])


def test_statistics_option(tmpdir, capsys):
    """Ensure that `flake8 --statistics` works."""
    with tmpdir.as_cwd():
        tmpdir.join('t.py').write('import os\nimport sys\n')
        _call_main(['--statistics', 't.py'], retv=1)

    out, err = capsys.readouterr()
    assert out == '''\
t.py:1:1: F401 'os' imported but unused
t.py:2:1: F401 'sys' imported but unused
2     F401 'os' imported but unused
'''
    assert err == ''


def test_extend_exclude(tmpdir, capsys):
    """Ensure that `flake8 --extend-exclude` works."""
    for d in ['project', 'vendor', 'legacy', '.git', '.tox', '.hg']:
        tmpdir.mkdir(d).join('t.py').write('import os\nimport sys\n')

    with tmpdir.as_cwd():
        _call_main(['--extend-exclude=vendor,legacy/'], retv=1)

    out, err = capsys.readouterr()
    expected_out = '''\
./project/t.py:1:1: F401 'os' imported but unused
./project/t.py:2:1: F401 'sys' imported but unused
'''
    assert out == expected_out.replace('/', os.sep)
    assert err == ''


def test_malformed_per_file_ignores_error(tmpdir, capsys):
    """Test the error message for malformed `per-file-ignores`."""
    setup_cfg = '''\
[flake8]
per-file-ignores =
    incorrect/*
    values/*
'''

    with tmpdir.as_cwd():
        tmpdir.join('setup.cfg').write(setup_cfg)
        _call_main(['.'], retv=1)

    out, err = capsys.readouterr()
    assert out == '''\
There was a critical error during execution of Flake8:
Expected `per-file-ignores` to be a mapping from file exclude patterns to ignore codes.

Configured `per-file-ignores` setting:

    incorrect/*
    values/*
'''  # noqa: E501


def test_tokenization_error_but_not_syntax_error(tmpdir, capsys):
    """Test that flake8 does not crash on tokenization errors."""
    with tmpdir.as_cwd():
        # this is a crash in the tokenizer, but not in the ast
        tmpdir.join('t.py').write("b'foo' \\\n")
        _call_main(['t.py'], retv=1)

    out, err = capsys.readouterr()
    assert out == 't.py:1:1: E902 TokenError: EOF in multi-line statement\n'
    assert err == ''


def test_tokenization_error_is_a_syntax_error(tmpdir, capsys):
    """Test when tokenize raises a SyntaxError."""
    with tmpdir.as_cwd():
        tmpdir.join('t.py').write('if True:\n    pass\n pass\n')
        _call_main(['t.py'], retv=1)

    out, err = capsys.readouterr()
    assert out == 't.py:1:1: E902 IndentationError: unindent does not match any outer indentation level\n'  # noqa: E501
    assert err == ''


def test_bug_report_successful(capsys):
    """Test that --bug-report does not crash."""
    _call_main(['--bug-report'])
    out, err = capsys.readouterr()
    assert json.loads(out)
    assert err == ''


def test_specific_noqa_does_not_clobber_pycodestyle_noqa(tmpdir, capsys):
    """See https://gitlab.com/pycqa/flake8/issues/552."""
    with tmpdir.as_cwd():
        tmpdir.join('t.py').write("test = ('ABC' == None)  # noqa: E501\n")
        _call_main(['t.py'], retv=1)

    out, err = capsys.readouterr()
    assert out == '''\
t.py:1:15: E711 comparison to None should be 'if cond is None:'
'''


def test_specific_noqa_on_line_with_continuation(tmpdir, capsys):
    """See https://gitlab.com/pycqa/flake8/issues/375."""
    t_py_src = '''\
from os \\
    import path  # noqa: F401

x = """
    trailing whitespace: \n
"""  # noqa: W291
'''

    with tmpdir.as_cwd():
        tmpdir.join('t.py').write(t_py_src)
        _call_main(['t.py'], retv=0)

    out, err = capsys.readouterr()
    assert out == err == ''


def test_obtaining_args_from_sys_argv_when_not_explicity_provided(capsys):
    """Test that arguments are obtained from 'sys.argv'."""
    with mock.patch('sys.argv', ['flake8', '--help']):
        _call_main(None)

    out, err = capsys.readouterr()
    assert out.startswith('usage: flake8 [options] file file ...\n')
    assert err == ''


def test_cli_config_option_respected(tmp_path):
    """Test --config is used."""
    config = tmp_path / "flake8.ini"
    config.write_text(u"""\
[flake8]
ignore = F401
""")

    py_file = tmp_path / "t.py"
    py_file.write_text(u"import os\n")

    _call_main(["--config", str(config), str(py_file)])


def test_cli_isolated_overrides_config_option(tmp_path):
    """Test --isolated overrides --config."""
    config = tmp_path / "flake8.ini"
    config.write_text(u"""\
[flake8]
ignore = F401
""")

    py_file = tmp_path / "t.py"
    py_file.write_text(u"import os\n")

    _call_main(["--isolated", "--config", str(config), str(py_file)], retv=1)


def test_file_not_found(tmpdir, capsys):
    """Ensure that a not-found file / directory is an error."""
    with tmpdir.as_cwd():
        _call_main(["i-do-not-exist"], retv=1)
    out, err = capsys.readouterr()
    assert out.startswith("i-do-not-exist:0:1: E902")
    assert err == ""


def test_output_file(tmpdir, capsys):
    """Ensure that --output-file is honored."""
    tmpdir.join('t.py').write('import os\n')

    with tmpdir.as_cwd():
        _call_main(['t.py', '--output-file=f'], retv=1)

    out, err = capsys.readouterr()
    assert out == err == ""

    expected = "t.py:1:1: F401 'os' imported but unused\n"
    assert tmpdir.join('f').read() == expected
