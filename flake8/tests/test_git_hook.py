import unittest
import mock

import flake8.hooks
import flake8.engine


def side_effect(command, raw_output=False, decode=False):
    if command.startswith("git diff-index") and not raw_output:
        return 0, ["ignore.py", "myproject/main.py",
                   "myproject/test/test.py"], []
    elif command.startswith("git show") and raw_output:
        return 0, "dummy standard output", "dummy standard error"
    else:
        raise NotImplementedError("side_effect")


def mock_open(read_data=""):
    #
    # mock_open from older versions of mock do not have readline
    #
    # There is a patch for this issue (http://bugs.python.org/issue17467).
    # I didn't use it directly since I needed readline to return None after all
    # lines have been read. The multiple None objects appended at the end
    # achieve this. I'm not sure why I need several -- one or two weren't
    # enough.
    #
    mo = mock.mock_open(read_data=read_data)
    lines = [x + "\n" for x in read_data.split("\n")] + [None]*10
    mo.return_value.readline.side_effect = lines
    return mo


class TestFixExclude(unittest.TestCase):
    """The scenario used to test fix_exclude is as follows.  There is a git
    repo with two files: ignore.py, myproject/main.py and
    myproject/test/test.py.  We want to run flake over myproject/main.py only.
    To achieve this, we add myproject/test/test.py to the list of exclude
    patterns -- in real life, this is done by editing configuration files
    (http://flake8.readthedocs.org/en/latest/config.html), but for the test we
    just mock it.

    Without the fix, since the exclude pattern for test.py contains a slash,
    pep8.read_config will convert it to an absolute path, using os.curdir as a
    base.  This behavior causes pep8.filename_match to fail, since our files
    will be in tmpdir, not os.curdir.  The end result is flake8 ends up
    checking myproject/test/test.py, which is something we don't want.

    With the fix, the exclude pattern is set correctly, and flake8 only checks
    one file: myproject/main.py.

    The exclude pattern for ignore.py is not affected by the fix, since it
    doesn't contain a slash, and isn't converted to an absolute path by
    pep8.read_config.
    """

    def setUp(self):
        self.config = "[flake8]\nexclude = ignore.py,myproject/test/test.py"

    @mock.patch("os.makedirs")
    @mock.patch.object(flake8.engine.StyleGuide, "check_files")
    @mock.patch("flake8.hooks.fix_exclude")
    @mock.patch("flake8.hooks.mkdtemp", return_value="/tmp")
    @mock.patch("flake8.hooks.run", side_effect=side_effect)
    def test_without_fix(self, mock_run, mock_mkdtemp, mock_fix_exclude,
                         mock_check_files, mock_makedirs):
        #
        # http://www.voidspace.org.uk/python/mock/helpers.html#mock.mock_open
        #
        with mock.patch("ConfigParser.open", mock_open(read_data=self.config),
                        create=True):
            with mock.patch("flake8.hooks.open", mock.mock_open(), create=True):
                flake8.hooks.git_hook()

        self.assertEquals(mock_check_files.call_count, 1)
        args = mock_check_files.call_args[0][0]
        print args
        self.assertEquals(len(args), 2)

    @mock.patch("os.makedirs")
    @mock.patch.object(flake8.engine.StyleGuide, "check_files")
    @mock.patch("flake8.hooks.mkdtemp", return_value="/tmp")
    @mock.patch("flake8.hooks.run", side_effect=side_effect)
    def test_with_fix(self, mock_run, mock_mkdtemp, mock_check_files,
                      mock_makedirs):
        #
        # http://www.voidspace.org.uk/python/mock/helpers.html#mock.mock_open
        #
        with mock.patch("ConfigParser.open", mock_open(read_data=self.config),
                        create=True):
            with mock.patch("flake8.hooks.open", mock.mock_open(), create=True):
                flake8.hooks.git_hook()

        self.assertEquals(mock_check_files.call_count, 1)
        args = mock_check_files.call_args[0][0]
        print args
        self.assertEquals(len(args), 1)
