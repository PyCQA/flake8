from __future__ import with_statement

import ast
import unittest

from collections import namedtuple

from flake8._pyflakes import FlakesChecker

Options = namedtuple("Options", ['builtins', 'doctests',
                                 'include_in_doctest',
                                 'exclude_from_doctest'])


class TestFlakesChecker(unittest.TestCase):

    def setUp(self):
        self.tree = ast.parse('print("cookies")')

    def test_doctest_flag_enabled(self):
        options = Options(builtins=None, doctests=True,
                          include_in_doctest='',
                          exclude_from_doctest='')
        FlakesChecker.parse_options(options)
        flake_checker = FlakesChecker(self.tree, 'cookies.txt')
        assert flake_checker.withDoctest is True

    def test_doctest_flag_disabled(self):
        options = Options(builtins=None, doctests=False,
                          include_in_doctest='',
                          exclude_from_doctest='')
        FlakesChecker.parse_options(options)
        flake_checker = FlakesChecker(self.tree, 'cookies.txt')
        assert flake_checker.withDoctest is False

    def test_doctest_flag_enabled_exclude_file(self):
        options = Options(builtins=None, doctests=True,
                          include_in_doctest='',
                          exclude_from_doctest='cookies.txt,'
                                               'hungry/cookies.txt')
        FlakesChecker.parse_options(options)
        flake_checker = FlakesChecker(self.tree, './cookies.txt')
        assert flake_checker.withDoctest is False

    def test_doctest_flag_disabled_include_file(self):
        options = Options(builtins=None, doctests=False,
                          include_in_doctest='./cookies.txt,cake_yuck.txt',
                          exclude_from_doctest='')
        FlakesChecker.parse_options(options)
        flake_checker = FlakesChecker(self.tree, './cookies.txt')
        assert flake_checker.withDoctest is True

    def test_doctest_flag_disabled_include_file_exclude_dir(self):
        options = Options(builtins=None, doctests=False,
                          include_in_doctest='./cookies.txt',
                          exclude_from_doctest='./')
        FlakesChecker.parse_options(options)
        flake_checker = FlakesChecker(self.tree, './cookies.txt')
        assert flake_checker.withDoctest is True

    def test_doctest_flag_disabled_include_dir_exclude_file(self):
        options = Options(builtins=None, doctests=False,
                          include_in_doctest='./',
                          exclude_from_doctest='./cookies.txt')
        FlakesChecker.parse_options(options)
        flake_checker = FlakesChecker(self.tree, './cookies.txt')
        assert flake_checker.withDoctest is False

    def test_doctest_flag_disabled_include_file_exclude_file_error(self):
        options = Options(builtins=None, doctests=False,
                          include_in_doctest='./cookies.txt',
                          exclude_from_doctest='./cookies.txt,cake_yuck.txt')
        self.assertRaises(ValueError, FlakesChecker.parse_options, options)
