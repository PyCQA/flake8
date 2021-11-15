import os.path

import pytest

from flake8 import utils
from flake8.discover_files import _filenames_from
from flake8.discover_files import expand_paths


@pytest.fixture
def files_dir(tmpdir):
    """Create test dir for testing filenames_from."""
    with tmpdir.as_cwd():
        tmpdir.join("a/b/c.py").ensure()
        tmpdir.join("a/b/d.py").ensure()
        tmpdir.join("a/b/e/f.py").ensure()
        yield tmpdir


def _noop(path):
    return False


def _normpath(s):
    return s.replace("/", os.sep)


def _normpaths(pths):
    return {_normpath(pth) for pth in pths}


@pytest.mark.usefixtures("files_dir")
def test_filenames_from_a_directory():
    """Verify that filenames_from walks a directory."""
    filenames = set(_filenames_from(_normpath("a/b/"), predicate=_noop))
    # should include all files
    expected = _normpaths(("a/b/c.py", "a/b/d.py", "a/b/e/f.py"))
    assert filenames == expected


@pytest.mark.usefixtures("files_dir")
def test_filenames_from_a_directory_with_a_predicate():
    """Verify that predicates filter filenames_from."""
    filenames = set(
        _filenames_from(
            arg=_normpath("a/b/"),
            predicate=lambda path: path.endswith(_normpath("b/c.py")),
        )
    )
    # should not include c.py
    expected = _normpaths(("a/b/d.py", "a/b/e/f.py"))
    assert filenames == expected


@pytest.mark.usefixtures("files_dir")
def test_filenames_from_a_directory_with_a_predicate_from_the_current_dir():
    """Verify that predicates filter filenames_from."""
    filenames = set(
        _filenames_from(
            arg=_normpath("./a/b"),
            predicate=lambda path: path == "c.py",
        )
    )
    # none should have matched the predicate so all returned
    expected = _normpaths(("./a/b/c.py", "./a/b/d.py", "./a/b/e/f.py"))
    assert filenames == expected


@pytest.mark.usefixtures("files_dir")
def test_filenames_from_a_single_file():
    """Verify that we simply yield that filename."""
    filenames = set(_filenames_from(_normpath("a/b/c.py"), predicate=_noop))
    assert filenames == {_normpath("a/b/c.py")}


def test_filenames_from_a_single_file_does_not_exist():
    """Verify that a passed filename which does not exist is returned back."""
    filenames = set(_filenames_from(_normpath("d/n/e.py"), predicate=_noop))
    assert filenames == {_normpath("d/n/e.py")}


def test_filenames_from_exclude_doesnt_exclude_directory_names(tmpdir):
    """Verify that we don't greedily exclude subdirs."""
    tmpdir.join("1/dont_return_me.py").ensure()
    tmpdir.join("2/1/return_me.py").ensure()
    exclude = [tmpdir.join("1").strpath]

    def predicate(pth):
        return utils.fnmatch(os.path.abspath(pth), exclude)

    with tmpdir.as_cwd():
        filenames = list(_filenames_from(".", predicate=predicate))
    assert filenames == [os.path.join(".", "2", "1", "return_me.py")]


def test_filenames_from_predicate_applies_to_initial_arg(tmp_path):
    """Test that the predicate is also applied to the passed argument."""
    fname = str(tmp_path.joinpath("f.py"))
    ret = tuple(_filenames_from(fname, predicate=lambda _: True))
    assert ret == ()


def test_filenames_from_predicate_applies_to_dirname(tmp_path):
    """Test that the predicate can filter whole directories."""
    a_dir = tmp_path.joinpath("a")
    a_dir.mkdir()
    a_dir.joinpath("b.py").touch()

    b_py = tmp_path.joinpath("b.py")
    b_py.touch()

    def predicate(p):
        # filter out the /a directory
        return p.endswith("a")

    ret = tuple(_filenames_from(str(tmp_path), predicate=predicate))
    assert ret == (str(b_py),)


def _expand_paths(
    *,
    paths=(".",),
    stdin_display_name="stdin",
    filename_patterns=("*.py",),
    exclude=(),
    is_running_from_diff=False,
):
    return set(
        expand_paths(
            paths=paths,
            stdin_display_name=stdin_display_name,
            filename_patterns=filename_patterns,
            exclude=exclude,
            is_running_from_diff=is_running_from_diff,
        )
    )


@pytest.mark.usefixtures("files_dir")
def test_expand_paths_honors_exclude():
    expected = _normpaths(("./a/b/c.py", "./a/b/e/f.py"))
    assert _expand_paths(exclude=["d.py"]) == expected


@pytest.mark.usefixtures("files_dir")
def test_expand_paths_defaults_to_dot():
    expected = _normpaths(("./a/b/c.py", "./a/b/d.py", "./a/b/e/f.py"))
    assert _expand_paths(paths=()) == expected


def test_default_stdin_name_is_not_filtered():
    assert _expand_paths(paths=("-",)) == {"-"}


def test_alternate_stdin_name_is_filtered():
    ret = _expand_paths(
        paths=("-",),
        stdin_display_name="wat",
        exclude=("wat",),
    )
    assert ret == set()


def test_filename_included_even_if_not_matching_include(tmp_path):
    some_file = str(tmp_path.joinpath("some/file"))
    assert _expand_paths(paths=(some_file,)) == {some_file}


def test_diff_filenames_filtered_by_patterns(tmp_path):
    f1 = str(tmp_path.joinpath("f1"))
    f2 = str(tmp_path.joinpath("f2.py"))

    ret = _expand_paths(paths=(f1, f2), is_running_from_diff=True)
    assert ret == {f2}
