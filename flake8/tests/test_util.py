import unittest
try:
    from unittest import mock
except ImportError:
    import mock  # < PY33

from flake8.util import option_normalizer

class TestOptionSerializer(unittest.TestCase):

    def test_true(self):
        option = option_normalizer('1')
        self.assertEqual(option, True)

        option = option_normalizer('T')
        self.assertEqual(option, True)

        option = option_normalizer('TRUE')
        self.assertEqual(option, True)

        option = option_normalizer('ON')
        self.assertEqual(option, True)

        option = option_normalizer('t')
        self.assertEqual(option, True)

        option = option_normalizer('true')
        self.assertEqual(option, True)

        option = option_normalizer('on')
        self.assertEqual(option, True)

    def test_false(self):
        option = option_normalizer('0')
        self.assertEqual(option, False)

        option = option_normalizer('F')
        self.assertEqual(option, False)

        option = option_normalizer('FALSE')
        self.assertEqual(option, False)

        option = option_normalizer('OFF')
        self.assertEqual(option, False)

        option = option_normalizer('f')
        self.assertEqual(option, False)

        option = option_normalizer('false')
        self.assertEqual(option, False)

        option = option_normalizer('off')
        self.assertEqual(option, False)

    def test_multiple_option(self):
        answer = ['F401', 'F402', 'F403', 'F404']

        option = option_normalizer('F401,F402,F403,F404')
        self.assertEqual(option, answer)

        option = option_normalizer('F401 ,F402 ,F403 ,F404')
        self.assertEqual(option, answer)

        option = option_normalizer('F401, F402, F403, F404')
        self.assertEqual(option, answer)

        option = option_normalizer('''\
            F401,
            F402,
            F403,
            F404,
        ''')
        self.assertEqual(option, answer)


if __name__ == '__main__':
    unittest.main()
