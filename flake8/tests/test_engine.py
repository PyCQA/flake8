from flake8 import engine
import unittest


class TestEngine(unittest.TestCase):
    def test_get_style_guide(self):
        g = engine.get_style_guide()
        self.assertTrue(isinstance(g, engine.StyleGuide))
