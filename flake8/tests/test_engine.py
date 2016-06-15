from __future__ import with_statement

import errno
import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

from flake8 import engine, util, __version__, reporter
import pycodestyle as pep8


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
            reg_ext.return_value = ([], [], [], [])
            g = engine.get_style_guide()
            self.assertTrue(isinstance(g, engine.StyleGuide))
            reg_ext.assert_called_once_with()

    def test_get_style_guide_kwargs(self):
        m = mock.Mock()
        with mock.patch('flake8.engine.StyleGuide') as StyleGuide:
            with mock.patch('flake8.engine.get_parser') as get_parser:
                m.ignored_extensions = []
                StyleGuide.return_value.options.jobs = '42'
                StyleGuide.return_value.options.diff = False
                get_parser.return_value = (m, [])
                engine.get_style_guide(foo='bar')
                get_parser.assert_called_once_with()
            StyleGuide.assert_called_once_with(**{'parser': m, 'foo': 'bar'})

    def test_register_extensions(self):
        with mock.patch('pycodestyle.register_check') as register_check:
            registered_exts = engine._register_extensions()
            self.assertTrue(isinstance(registered_exts[0], util.OrderedSet))
            self.assertTrue(len(registered_exts[0]) > 0)
            for i in registered_exts[1:]:
                self.assertTrue(isinstance(i, list))
            self.assertTrue(register_check.called)

    def test_disable_extensions(self):
        parser = mock.MagicMock()
        options = mock.MagicMock()

        parser.ignored_extensions = ['I123', 'I345', 'I678', 'I910']

        options.enable_extensions = 'I345,\nI678,I910'
        options.ignore = ('E121', 'E123')

        engine._disable_extensions(parser, options)
        self.assertEqual(set(options.ignore), set(['E121', 'E123', 'I123']))

    def test_get_parser(self):
        # setup
        re = self.start_patch('flake8.engine._register_extensions')
        gpv = self.start_patch('flake8.engine.get_python_version')
        pgp = self.start_patch('pycodestyle.get_parser')
        m = mock.Mock()
        re.return_value = ([('pyflakes', '0.7'), ('mccabe', '0.2')], [], [],
                           [])
        gpv.return_value = 'Python Version'
        pgp.return_value = m
        # actual call we're testing
        parser, hooks = engine.get_parser()
        # assertions
        self.assertTrue(re.called)
        self.assertTrue(gpv.called)
        pgp.assert_called_once_with(
            'flake8',
            '%s (pyflakes: 0.7, mccabe: 0.2) Python Version' % __version__)
        self.assertTrue(m.remove_option.called)
        self.assertTrue(m.add_option.called)
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
        with mock.patch('flake8.util.is_windows') as is_windows:
            is_windows.return_value = True
            guide = engine.get_style_guide()
            assert isinstance(guide, reporter.BaseQReport) is False

    def test_stdin_disables_jobs(self):
        with mock.patch('flake8.util.is_using_stdin') as is_using_stdin:
            is_using_stdin.return_value = True
            guide = engine.get_style_guide()
            assert isinstance(guide, reporter.BaseQReport) is False

    def test_disables_extensions_that_are_not_selected(self):
        with mock.patch('flake8.engine._register_extensions') as re:
            re.return_value = ([('fake_ext', '0.1a1')], [], [], ['X'])
            sg = engine.get_style_guide()
            assert 'X' in sg.options.ignore

    def test_enables_off_by_default_extensions(self):
        with mock.patch('flake8.engine._register_extensions') as re:
            re.return_value = ([('fake_ext', '0.1a1')], [], [], ['X'])
            parser, options = engine.get_parser()
            parser.parse_args(['--select=X'])
            sg = engine.StyleGuide(parser=parser)
            assert 'X' not in sg.options.ignore

    def test_load_entry_point_verifies_requirements(self):
        entry_point = mock.Mock(spec=['require', 'resolve', 'load'])

        engine._load_entry_point(entry_point, verify_requirements=True)
        entry_point.require.assert_called_once_with()
        entry_point.resolve.assert_called_once_with()

    def test_load_entry_point_does_not_verify_requirements(self):
        entry_point = mock.Mock(spec=['require', 'resolve', 'load'])

        engine._load_entry_point(entry_point, verify_requirements=False)
        self.assertFalse(entry_point.require.called)
        entry_point.resolve.assert_called_once_with()

    def test_load_entry_point_passes_require_argument_to_load(self):
        entry_point = mock.Mock(spec=['load'])

        engine._load_entry_point(entry_point, verify_requirements=True)
        entry_point.load.assert_called_once_with(require=True)
        entry_point.reset_mock()

        engine._load_entry_point(entry_point, verify_requirements=False)
        entry_point.load.assert_called_once_with(require=False)


def oserror_generator(error_number, message='Ominous OSError message'):
    def oserror_side_effect(*args, **kwargs):
        if hasattr(oserror_side_effect, 'used'):
            return

        oserror_side_effect.used = True
        raise OSError(error_number, message)

    return oserror_side_effect


class TestStyleGuide(unittest.TestCase):
    def setUp(self):
        mocked_styleguide = mock.Mock(spec=engine.NoQAStyleGuide)
        self.styleguide = engine.StyleGuide(styleguide=mocked_styleguide)
        self.mocked_sg = mocked_styleguide

    def test_proxies_excluded(self):
        self.styleguide.excluded('file.py', parent='.')

        self.mocked_sg.excluded.assert_called_once_with('file.py', parent='.')

    def test_proxies_init_report(self):
        reporter = object()
        self.styleguide.init_report(reporter)

        self.mocked_sg.init_report.assert_called_once_with(reporter)

    def test_proxies_check_files(self):
        self.styleguide.check_files(['foo', 'bar'])

        self.mocked_sg.check_files.assert_called_once_with(
            paths=['foo', 'bar']
        )

    def test_proxies_input_file(self):
        self.styleguide.input_file('file.py',
                                   lines=[9, 10],
                                   expected='foo',
                                   line_offset=20)

        self.mocked_sg.input_file.assert_called_once_with(filename='file.py',
                                                          lines=[9, 10],
                                                          expected='foo',
                                                          line_offset=20)

    def test_check_files_retries_on_specific_OSErrors(self):
        self.mocked_sg.check_files.side_effect = oserror_generator(
            errno.ENOSPC, 'No space left on device'
        )

        self.styleguide.check_files(['foo', 'bar'])

        self.mocked_sg.init_report.assert_called_once_with(pep8.StandardReport)

    def test_input_file_retries_on_specific_OSErrors(self):
        self.mocked_sg.input_file.side_effect = oserror_generator(
            errno.ENOSPC, 'No space left on device'
        )

        self.styleguide.input_file('file.py')

        self.mocked_sg.init_report.assert_called_once_with(pep8.StandardReport)

    def test_check_files_reraises_unknown_OSErrors(self):
        self.mocked_sg.check_files.side_effect = oserror_generator(
            errno.EADDRINUSE,
            'lol why are we talking about binding to sockets'
        )

        self.assertRaises(OSError, self.styleguide.check_files,
                          ['foo', 'bar'])

    def test_input_file_reraises_unknown_OSErrors(self):
        self.mocked_sg.input_file.side_effect = oserror_generator(
            errno.EADDRINUSE,
            'lol why are we talking about binding to sockets'
        )

        self.assertRaises(OSError, self.styleguide.input_file,
                          ['foo', 'bar'])

if __name__ == '__main__':
    unittest.main()
