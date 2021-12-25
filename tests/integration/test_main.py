"""Integration tests for the main entrypoint of flake8."""
import json
import os
import sys
from unittest import mock

import pytest

from flake8 import utils
from flake8.main import cli
from flake8.options import config


def test_diff_option(tmpdir, capsys):
    """Ensure that `flake8 --diff` works."""
    t_py_contents = """\
import os
import sys  # unused but not part of diff

print('(to avoid trailing whitespace in test)')
print('(to avoid trailing whitespace in test)')
print(os.path.join('foo', 'bar'))

y  # part of the diff and an error
"""

    diff = """\
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
"""

    with mock.patch.object(utils, "stdin_get_value", return_value=diff):
        with tmpdir.as_cwd():
            tmpdir.join("t.py").write(t_py_contents)
            assert cli.main(["--diff"]) == 1

    out, err = capsys.readouterr()
    assert out == "t.py:8:1: F821 undefined name 'y'\n"
    assert err == ""


def test_form_feed_line_split(tmpdir, capsys):
    """Test that form feed is treated the same for stdin."""
    src = "x=1\n\f\ny=1\n"
    expected_out = """\
t.py:1:2: E225 missing whitespace around operator
t.py:3:2: E225 missing whitespace around operator
"""

    with tmpdir.as_cwd():
        tmpdir.join("t.py").write(src)

        with mock.patch.object(utils, "stdin_get_value", return_value=src):
            assert cli.main(["-", "--stdin-display-name=t.py"]) == 1
            out, err = capsys.readouterr()
            assert out == expected_out
            assert err == ""

        assert cli.main(["t.py"]) == 1
        out, err = capsys.readouterr()
        assert out == expected_out
        assert err == ""


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
        tmpdir.join("t.py").write(t_py_contents)
        assert cli.main(["t.py"]) == 0


def test_statistics_option(tmpdir, capsys):
    """Ensure that `flake8 --statistics` works."""
    with tmpdir.as_cwd():
        tmpdir.join("t.py").write("import os\nimport sys\n")
        assert cli.main(["--statistics", "t.py"]) == 1

    expected = """\
t.py:1:1: F401 'os' imported but unused
t.py:2:1: F401 'sys' imported but unused
2     F401 'os' imported but unused
"""
    out, err = capsys.readouterr()
    assert out == expected
    assert err == ""


def test_show_source_option(tmpdir, capsys):
    """Ensure that --show-source and --no-show-source work."""
    with tmpdir.as_cwd():
        tmpdir.join("tox.ini").write("[flake8]\nshow_source = true\n")
        tmpdir.join("t.py").write("import os\n")
        assert cli.main(["t.py"]) == 1

    expected = """\
t.py:1:1: F401 'os' imported but unused
import os
^
"""
    out, err = capsys.readouterr()
    assert out == expected
    assert err == ""

    with tmpdir.as_cwd():
        assert cli.main(["t.py", "--no-show-source"]) == 1

    expected = """\
t.py:1:1: F401 'os' imported but unused
"""
    out, err = capsys.readouterr()
    assert out == expected
    assert err == ""


def test_extend_exclude(tmpdir, capsys):
    """Ensure that `flake8 --extend-exclude` works."""
    for d in ["project", "vendor", "legacy", ".git", ".tox", ".hg"]:
        tmpdir.mkdir(d).join("t.py").write("import os\nimport sys\n")

    with tmpdir.as_cwd():
        assert cli.main(["--extend-exclude=vendor,legacy/"]) == 1

    out, err = capsys.readouterr()
    expected_out = """\
./project/t.py:1:1: F401 'os' imported but unused
./project/t.py:2:1: F401 'sys' imported but unused
"""
    assert out == expected_out.replace("/", os.sep)
    assert err == ""


def test_malformed_per_file_ignores_error(tmpdir, capsys):
    """Test the error message for malformed `per-file-ignores`."""
    setup_cfg = """\
[flake8]
per-file-ignores =
    incorrect/*
    values/*
"""
    expected = """\
There was a critical error during execution of Flake8:
Expected `per-file-ignores` to be a mapping from file exclude patterns to ignore codes.

Configured `per-file-ignores` setting:

    incorrect/*
    values/*
"""  # noqa: E501

    with tmpdir.as_cwd():
        tmpdir.join("setup.cfg").write(setup_cfg)
        assert cli.main(["."]) == 1

    out, err = capsys.readouterr()
    assert out == expected


def test_tokenization_error_but_not_syntax_error(tmpdir, capsys):
    """Test that flake8 does not crash on tokenization errors."""
    with tmpdir.as_cwd():
        # this is a crash in the tokenizer, but not in the ast
        tmpdir.join("t.py").write("b'foo' \\\n")
        assert cli.main(["t.py"]) == 1

    if hasattr(sys, "pypy_version_info"):  # pragma: no cover (pypy)
        expected = "t.py:2:1: E999 SyntaxError: end of file (EOF) in multi-line statement\n"  # noqa: E501
    elif sys.version_info < (3, 8):  # pragma: no cover (<cp38)
        expected = "t.py:2:1: E902 TokenError: EOF in multi-line statement\n"
    elif sys.version_info < (3, 10):  # pragma: no cover (cp38+)
        expected = "t.py:1:8: E999 SyntaxError: unexpected EOF while parsing\n"
    else:  # pragma: no cover (cp310+)
        expected = "t.py:1:10: E999 SyntaxError: unexpected EOF while parsing\n"  # noqa: E501

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ""


def test_tokenization_error_is_a_syntax_error(tmpdir, capsys):
    """Test when tokenize raises a SyntaxError."""
    with tmpdir.as_cwd():
        tmpdir.join("t.py").write("if True:\n    pass\n pass\n")
        assert cli.main(["t.py"]) == 1

    if hasattr(sys, "pypy_version_info"):  # pragma: no cover (pypy)
        expected = "t.py:3:2: E999 IndentationError: unindent does not match any outer indentation level\n"  # noqa: E501
    elif sys.version_info < (3, 10):  # pragma: no cover (<cp310)
        expected = "t.py:3:5: E999 IndentationError: unindent does not match any outer indentation level\n"  # noqa: E501
    else:  # pragma: no cover (cp310+)
        expected = "t.py:3:7: E999 IndentationError: unindent does not match any outer indentation level\n"  # noqa: E501

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ""


def test_bug_report_successful(capsys):
    """Test that --bug-report does not crash."""
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--bug-report"])
    assert excinfo.value.args[0] == 0
    out, err = capsys.readouterr()
    assert json.loads(out)
    assert err == ""


def test_benchmark_successful(tmp_path, capsys):
    """Test that --benchmark does not crash."""
    fname = tmp_path.joinpath("t.py")
    fname.write_text("print('hello world')\n")

    assert cli.main(["--benchmark", str(fname)]) == 0

    out, err = capsys.readouterr()
    parts = [line.split(maxsplit=1) for line in out.splitlines()]
    assert parts == [
        [mock.ANY, "seconds elapsed"],
        ["1", "total logical lines processed"],
        [mock.ANY, "logical lines processed per second"],
        ["1", "total physical lines processed"],
        [mock.ANY, "physical lines processed per second"],
        ["5", "total tokens processed"],
        [mock.ANY, "tokens processed per second"],
        ["1", "total files processed"],
        [mock.ANY, "files processed per second"],
    ]
    assert err == ""


def test_specific_noqa_does_not_clobber_pycodestyle_noqa(tmpdir, capsys):
    """See https://github.com/pycqa/flake8/issues/1104."""
    with tmpdir.as_cwd():
        tmpdir.join("t.py").write("test = ('ABC' == None)  # noqa: E501\n")
        assert cli.main(["t.py"]) == 1

    expected = """\
t.py:1:15: E711 comparison to None should be 'if cond is None:'
"""
    out, err = capsys.readouterr()
    assert out == expected


def test_specific_noqa_on_line_with_continuation(tmpdir, capsys):
    """See https://github.com/pycqa/flake8/issues/621."""
    t_py_src = '''\
from os \\
    import path  # noqa: F401

x = """
    trailing whitespace: \n
"""  # noqa: W291
'''

    with tmpdir.as_cwd():
        tmpdir.join("t.py").write(t_py_src)
        assert cli.main(["t.py"]) == 0

    out, err = capsys.readouterr()
    assert out == err == ""


def test_physical_line_file_not_ending_in_newline(tmpdir, capsys):
    """See https://github.com/PyCQA/pycodestyle/issues/960."""
    t_py_src = "def f():\n\tpass"

    with tmpdir.as_cwd():
        tmpdir.join("t.py").write(t_py_src)
        assert cli.main(["t.py"]) == 1

    expected = """\
t.py:2:1: W191 indentation contains tabs
t.py:2:6: W292 no newline at end of file
"""
    out, err = capsys.readouterr()
    assert out == expected


def test_physical_line_file_not_ending_in_newline_trailing_ws(tmpdir, capsys):
    """See https://github.com/PyCQA/pycodestyle/issues/960."""
    t_py_src = "x = 1   "

    with tmpdir.as_cwd():
        tmpdir.join("t.py").write(t_py_src)
        assert cli.main(["t.py"]) == 1

    expected = """\
t.py:1:6: W291 trailing whitespace
t.py:1:9: W292 no newline at end of file
"""
    out, err = capsys.readouterr()
    assert out == expected


def test_obtaining_args_from_sys_argv_when_not_explicity_provided(capsys):
    """Test that arguments are obtained from 'sys.argv'."""
    with mock.patch("sys.argv", ["flake8", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            cli.main()
    assert excinfo.value.args[0] == 0

    out, err = capsys.readouterr()
    assert out.startswith("usage: flake8 [options] file file ...\n")
    assert err == ""


def test_cli_config_option_respected(tmp_path):
    """Test --config is used."""
    config = tmp_path / "flake8.ini"
    config.write_text(
        """\
[flake8]
ignore = F401
"""
    )

    py_file = tmp_path / "t.py"
    py_file.write_text("import os\n")

    assert cli.main(["--config", str(config), str(py_file)]) == 0


def test_cli_isolated_overrides_config_option(tmp_path):
    """Test --isolated overrides --config."""
    config = tmp_path / "flake8.ini"
    config.write_text(
        """\
[flake8]
ignore = F401
"""
    )

    py_file = tmp_path / "t.py"
    py_file.write_text("import os\n")

    assert cli.main(["--isolated", "--config", str(config), str(py_file)]) == 1


def test_file_not_found(tmpdir, capsys):
    """Ensure that a not-found file / directory is an error."""
    with tmpdir.as_cwd():
        assert cli.main(["i-do-not-exist"]) == 1
    out, err = capsys.readouterr()
    assert out.startswith("i-do-not-exist:0:1: E902")
    assert err == ""


def test_output_file(tmpdir, capsys):
    """Ensure that --output-file is honored."""
    tmpdir.join("t.py").write("import os\n")

    with tmpdir.as_cwd():
        assert cli.main(["t.py", "--output-file=a/b/f"]) == 1

    out, err = capsys.readouterr()
    assert out == err == ""

    expected = "t.py:1:1: F401 'os' imported but unused\n"
    assert tmpdir.join("a/b/f").read() == expected


def test_early_keyboard_interrupt_does_not_crash(capsys):
    with mock.patch.object(
        config, "load_config", side_effect=KeyboardInterrupt
    ):
        assert cli.main(["does-not-exist"]) == 1
    out, err = capsys.readouterr()
    assert out == "... stopped\n"
    assert err == ""


def test_config_file_not_found(tmpdir, capsys):
    """Ensure that an explicitly specified config file which is not found is an
    error"""

    expected = """\
There was a critical error during execution of Flake8:
The specified config file does not exist: missing.cfg
"""

    with tmpdir.as_cwd():
        tmpdir.join("t.py").write("print('hello hello world')\n")
        assert cli.main(["--config", "missing.cfg", "t.py"]) == 1

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ""
