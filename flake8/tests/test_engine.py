from flake8 import engine
import unittest
import mock


class TestEngine(unittest.TestCase):
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
                get_parser.return_value = (m, [])
                engine.get_style_guide(foo='bar')
                get_parser.assert_called_once_with()
            StyleGuide.assert_called_once_with(**{'parser': m, 'foo': 'bar'})
