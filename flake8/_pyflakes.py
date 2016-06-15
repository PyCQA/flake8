# -*- coding: utf-8 -*-
try:
    # The 'demandimport' breaks pyflakes and flake8._pyflakes
    from mercurial import demandimport
except ImportError:
    pass
else:
    demandimport.disable()
import os

import pycodestyle as pep8
import pyflakes
import pyflakes.checker


def patch_pyflakes():
    """Add error codes to Pyflakes messages."""
    codes = dict([line.split()[::-1] for line in (
        'F401 UnusedImport',
        'F402 ImportShadowedByLoopVar',
        'F403 ImportStarUsed',
        'F404 LateFutureImport',
        'F405 ImportStarUsage',
        'F810 Redefined',               # XXX Obsolete?
        'F811 RedefinedWhileUnused',
        'F812 RedefinedInListComp',
        'F821 UndefinedName',
        'F822 UndefinedExport',
        'F823 UndefinedLocal',
        'F831 DuplicateArgument',
        'F841 UnusedVariable',
    )])

    for name, obj in vars(pyflakes.messages).items():
        if name[0].isupper() and obj.message:
            obj.flake8_msg = '%s %s' % (codes.get(name, 'F999'), obj.message)
patch_pyflakes()


class FlakesChecker(pyflakes.checker.Checker):
    """Subclass the Pyflakes checker to conform with the flake8 API."""
    name = 'pyflakes'
    version = pyflakes.__version__

    def __init__(self, tree, filename):
        filename = pep8.normalize_paths(filename)[0]
        withDoctest = self.withDoctest
        included_by = [include for include in self.include_in_doctest
                       if include != '' and filename.startswith(include)]
        if included_by:
            withDoctest = True

        for exclude in self.exclude_from_doctest:
            if exclude != '' and filename.startswith(exclude):
                withDoctest = False
                overlaped_by = [include for include in included_by
                                if include.startswith(exclude)]

                if overlaped_by:
                    withDoctest = True

        super(FlakesChecker, self).__init__(tree, filename,
                                            withDoctest=withDoctest)

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--builtins',
                          help="define more built-ins, comma separated")
        parser.add_option('--doctests', default=False, action='store_true',
                          help="check syntax of the doctests")
        parser.add_option('--include-in-doctest', default='',
                          dest='include_in_doctest',
                          help='Run doctests only on these files',
                          type='string')
        parser.add_option('--exclude-from-doctest', default='',
                          dest='exclude_from_doctest',
                          help='Skip these files when running doctests',
                          type='string')
        parser.config_options.extend(['builtins', 'doctests',
                                      'include-in-doctest',
                                      'exclude-from-doctest'])

    @classmethod
    def parse_options(cls, options):
        if options.builtins:
            cls.builtIns = cls.builtIns.union(options.builtins.split(','))
        cls.withDoctest = options.doctests

        included_files = []
        for included_file in options.include_in_doctest.split(','):
            if included_file == '':
                continue
            if not included_file.startswith((os.sep, './', '~/')):
                included_files.append('./' + included_file)
            else:
                included_files.append(included_file)
        cls.include_in_doctest = pep8.normalize_paths(','.join(included_files))

        excluded_files = []
        for excluded_file in options.exclude_from_doctest.split(','):
            if excluded_file == '':
                continue
            if not excluded_file.startswith((os.sep, './', '~/')):
                excluded_files.append('./' + excluded_file)
            else:
                excluded_files.append(excluded_file)
        cls.exclude_from_doctest = pep8.normalize_paths(
            ','.join(excluded_files))

        inc_exc = set(cls.include_in_doctest).intersection(
            set(cls.exclude_from_doctest))
        if inc_exc:
            raise ValueError('"%s" was specified in both the '
                             'include-in-doctest and exclude-from-doctest '
                             'options. You are not allowed to specify it in '
                             'both for doctesting.' % inc_exc)

    def run(self):
        for m in self.messages:
            col = getattr(m, 'col', 0)
            yield m.lineno, col, (m.flake8_msg % m.message_args), m.__class__
