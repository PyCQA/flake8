"""Constants that define defaults."""

EXCLUDE = '.svn,CVS,.bzr,.hg,.git,__pycache__,.tox'
IGNORE = 'E121,E123,E126,E226,E24,E704,W503,W504'
SELECT = 'E,F,W,C'
MAX_LINE_LENGTH = 79

TRUTHY_VALUES = set(['true', '1', 't'])

# Other constants
WHITESPACE = frozenset(' \t')

STATISTIC_NAMES = (
    'logical lines',
    'physical lines',
    'tokens',
)
