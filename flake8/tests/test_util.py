import unittest

from flake8.util import option_normalizer


class TestOptionSerializer(unittest.TestCase):

    def test_1_is_true(self):
        option = option_normalizer('1')
        self.assertTrue(option)

    def test_T_is_true(self):
        option = option_normalizer('T')
        self.assertTrue(option)

    def test_TRUE_is_true(self):
        option = option_normalizer('TRUE')
        self.assertTrue(option, True)

    def test_ON_is_true(self):
        option = option_normalizer('ON')
        self.assertTrue(option)

    def test_t_is_true(self):
        option = option_normalizer('t')
        self.assertTrue(option)

    def test_true_is_true(self):
        option = option_normalizer('true')
        self.assertTrue(option)

    def test_on_is_true(self):
        option = option_normalizer('on')
        self.assertTrue(option)

    def test_0_is_false(self):
        option = option_normalizer('0')
        self.assertFalse(option)

    def test_F_is_false(self):
        option = option_normalizer('F')
        self.assertFalse(option)

    def test_FALSE_is_false(self):
        option = option_normalizer('FALSE')
        self.assertFalse(option)

    def test_OFF_is_false(self):
        option = option_normalizer('OFF')
        self.assertFalse(option)

    def test_f_is_false(self):
        option = option_normalizer('f')
        self.assertFalse(option)

    def test_false_is_false(self):
        option = option_normalizer('false')
        self.assertFalse(option)

    def test_off_is_false(self):
        option = option_normalizer('off')
        self.assertFalse(option)

    def test_parses_lists(self):
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
