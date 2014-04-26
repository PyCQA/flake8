# -*- coding: utf-8 -*-
try:
    # The 'demandimport' breaks pyflakes and flake8._pyflakes
    from mercurial import demandimport
except ImportError:
    pass
else:
    demandimport.disable()
import pyflakes
import pyflakes.checker


def patch_pyflakes():
    """Add error codes to Pyflakes messages."""
    codes = dict([line.split()[::-1] for line in (
        'F401 UnusedImport',
        'F402 ImportShadowedByLoopVar',
        'F403 ImportStarUsed',
        'F404 LateFutureImport',
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
        super(FlakesChecker, self).__init__(tree, filename,
                                            withDoctest=self.withDoctest)

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--builtins',
                          help="define more built-ins, comma separated")
        parser.add_option('--doctests', default=False, action='store_true',
                          help="check syntax of the doctests")
        parser.config_options.extend(['builtins', 'doctests'])

    @classmethod
    def parse_options(cls, options):
        if options.builtins:
            cls.builtIns = cls.builtIns.union(options.builtins.split(','))
        cls.withDoctest = options.doctests

    def run(self):
        for m in self.messages:
            col = getattr(m, 'col', 0)
            yield m.lineno, col, (m.flake8_msg % m.message_args), m.__class__
