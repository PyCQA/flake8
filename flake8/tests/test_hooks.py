"""Module containing the tests for flake8.hooks."""
import os
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import flake8.hooks


def excluded(filename):
    return filename.endswith('afile.py')


class TestGitHook(unittest.TestCase):
    @mock.patch('os.makedirs')
    @mock.patch('flake8.hooks.open', create=True)
    @mock.patch('shutil.rmtree')
    @mock.patch('tempfile.mkdtemp', return_value='/fake/tmp')
    @mock.patch('flake8.hooks.run',
                return_value=(None, ['foo/afile.py', 'foo/bfile.py'], None))
    @mock.patch('flake8.hooks.get_style_guide')
    def test_prepends_tmp_directory_to_exclude(self, get_style_guide, run,
                                               *args):
        style_guide = get_style_guide.return_value = mock.Mock()
        style_guide.options.exclude = ['foo/afile.py']
        style_guide.options.filename = ['foo/*']
        style_guide.excluded = excluded

        flake8.hooks.git_hook()

        dirname, filename = os.path.split(os.path.abspath('foo/bfile.py'))
        tmpdir = os.path.join('/fake/tmp', dirname[1:])
        tmpfile = os.path.join(tmpdir, 'bfile.py')
        style_guide.check_files.assert_called_once_with([tmpfile])


if __name__ == '__main__':
    unittest.main()
