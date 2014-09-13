from __future__ import with_statement

import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

from flake8 import engine, util, __version__, reporter


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.patches = {}

    def tearDown(self):
        assert len(self.patches.items()) == 0

    def start_patch(self, patch):
        self.patches[patch] = mock.patch(patch)
        return self.patches[patch].start()

    def stop_patches(self):
        patches = self.patches.copy()
        for k, v in patches.items():
            v.stop()
            del(self.patches[k])

    def test_get_style_guide(self):
        with mock.patch('flake8.engine._register_extensions') as reg_ext:
            reg_ext.return_value = ([], [], [])
            g = engine.get_style_guide()
            self.assertTrue(isinstance(g, engine.StyleGuide))
            reg_ext.assert_called_once_with()

    def test_get_style_guide_kwargs(self):
        m = mock.Mock()
        with mock.patch('flake8.engine.StyleGuide') as StyleGuide:
            with mock.patch('flake8.engine.get_parser') as get_parser:
                StyleGuide.return_value.options.jobs = '42'
                get_parser.return_value = (m, [])
                engine.get_style_guide(foo='bar')
                get_parser.assert_called_once_with()
            StyleGuide.assert_called_once_with(**{'parser': m, 'foo': 'bar'})

    def test_register_extensions(self):
        with mock.patch('pep8.register_check') as register_check:
            registered_exts = engine._register_extensions()
            self.assertTrue(isinstance(registered_exts[0], util.OrderedSet))
            self.assertTrue(len(registered_exts[0]) > 0)
            for i in registered_exts[1:]:
                self.assertTrue(isinstance(i, list))
            register_check.assert_called()

    def test_get_parser(self):
        # setup
        re = self.start_patch('flake8.engine._register_extensions')
        gpv = self.start_patch('flake8.engine.get_python_version')
        pgp = self.start_patch('pep8.get_parser')
        m = mock.Mock()
        re.return_value = ([('pyflakes', '0.7'), ('mccabe', '0.2')], [], [])
        gpv.return_value = 'Python Version'
        pgp.return_value = m
        # actual call we're testing
        parser, hooks = engine.get_parser()
        # assertions
        re.assert_called()
        gpv.assert_called()
        pgp.assert_called_once_with(
            'flake8',
            '%s (pyflakes: 0.7, mccabe: 0.2) Python Version' % __version__)
        m.remove_option.assert_called()
        m.add_option.assert_called()
        self.assertEqual(parser, m)
        self.assertEqual(hooks, [])
        # clean-up
        self.stop_patches()

    def test_get_python_version(self):
        self.assertTrue('on' in engine.get_python_version())
        # Silly test but it will provide 100% test coverage
        # Also we can never be sure (without reconstructing the string
        # ourselves) what system we may be testing on.

    def test_windows_disables_jobs(self):
        with mock.patch('flake8.engine.is_windows') as is_windows:
            is_windows.return_value = True
            guide = engine.get_style_guide()
            assert isinstance(guide, reporter.BaseQReport) is False

    def test_stdin_disables_jobs(self):
        with mock.patch('flake8.engine.is_using_stdin') as is_using_stdin:
            is_using_stdin.return_value = True
            guide = engine.get_style_guide()
            assert isinstance(guide, reporter.BaseQReport) is False

if __name__ == '__main__':
    unittest.main()
