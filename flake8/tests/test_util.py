import optparse
import unittest

from flake8.util import option_normalizer


class TestOptionSerializerParsesTrue(unittest.TestCase):

    def setUp(self):
        self.option = optparse.Option('--foo', action='store_true')
        self.option_name = 'fake_option'

    def test_1_is_true(self):
        value = option_normalizer('1', self.option, self.option_name)
        self.assertTrue(value)

    def test_T_is_true(self):
        value = option_normalizer('T', self.option, self.option_name)
        self.assertTrue(value)

    def test_TRUE_is_true(self):
        value = option_normalizer('TRUE', self.option, self.option_name)
        self.assertTrue(value, True)

    def test_ON_is_true(self):
        value = option_normalizer('ON', self.option, self.option_name)
        self.assertTrue(value)

    def test_t_is_true(self):
        value = option_normalizer('t', self.option, self.option_name)
        self.assertTrue(value)

    def test_true_is_true(self):
        value = option_normalizer('true', self.option, self.option_name)
        self.assertTrue(value)

    def test_on_is_true(self):
        value = option_normalizer('on', self.option, self.option_name)
        self.assertTrue(value)


class TestOptionSerializerParsesFalse(unittest.TestCase):

    def setUp(self):
        self.option = optparse.Option('--foo', action='store_true')
        self.option_name = 'fake_option'

    def test_0_is_false(self):
        value = option_normalizer('0', self.option, self.option_name)
        self.assertFalse(value)

    def test_F_is_false(self):
        value = option_normalizer('F', self.option, self.option_name)
        self.assertFalse(value)

    def test_FALSE_is_false(self):
        value = option_normalizer('FALSE', self.option, self.option_name)
        self.assertFalse(value)

    def test_OFF_is_false(self):
        value = option_normalizer('OFF', self.option, self.option_name)
        self.assertFalse(value)

    def test_f_is_false(self):
        value = option_normalizer('f', self.option, self.option_name)
        self.assertFalse(value)

    def test_false_is_false(self):
        value = option_normalizer('false', self.option, self.option_name)
        self.assertFalse(value)

    def test_off_is_false(self):
        value = option_normalizer('off', self.option, self.option_name)
        self.assertFalse(value)


class TestOptionSerializerParsesLists(unittest.TestCase):

    def setUp(self):
        self.option = optparse.Option('--select')
        self.option_name = 'select'
        self.answer = ['F401', 'F402', 'F403', 'F404', 'F405']

    def test_parses_simple_comma_separated_lists(self):
        value = option_normalizer('F401,F402,F403,F404,F405', self.option,
                                  self.option_name)
        self.assertEqual(value, self.answer)

    def test_parses_less_simple_comma_separated_lists(self):
        value = option_normalizer('F401 ,F402 ,F403 ,F404, F405', self.option,
                                  self.option_name)
        self.assertEqual(value, self.answer)

        value = option_normalizer('F401, F402, F403, F404, F405', self.option,
                                  self.option_name)
        self.assertEqual(value, self.answer)

    def test_parses_comma_separated_lists_with_newlines(self):
        value = option_normalizer('''\
            F401,
            F402,
            F403,
            F404,
            F405,
        ''', self.option, self.option_name)
        self.assertEqual(value, self.answer)


class TestOptionSerializerParsesInts(unittest.TestCase):

    def setUp(self):
        self.option = optparse.Option('--max-complexity', type='int')
        self.option_name = 'max_complexity'

    def test_parses_an_int(self):
        value = option_normalizer('2', self.option, self.option_name)
        self.assertEqual(value, 2)


if __name__ == '__main__':
    unittest.main()
