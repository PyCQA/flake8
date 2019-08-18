"""Tests for the flake8.style_guide.DecisionEngine class."""
import argparse

import pytest

from flake8 import defaults
from flake8 import style_guide


def create_options(**kwargs):
    """Create and return an instance of argparse.Namespace."""
    kwargs.setdefault('select', [])
    kwargs.setdefault('extended_default_select', [])
    kwargs.setdefault('ignore', [])
    kwargs.setdefault('extend_ignore', [])
    kwargs.setdefault('disable_noqa', False)
    kwargs.setdefault('enable_extensions', [])
    return argparse.Namespace(**kwargs)


@pytest.mark.parametrize('ignore_list,extend_ignore,error_code', [
    (['E111', 'E121'], [], 'E111'),
    (['E111', 'E121'], [], 'E121'),
    (['E111'], ['E121'], 'E121'),
    (['E11', 'E12'], [], 'E121'),
    (['E2', 'E12'], [], 'E121'),
    (['E2', 'E12'], [], 'E211'),
    (['E2', 'E3'], ['E12'], 'E211'),
])
def test_was_ignored_ignores_errors(ignore_list, extend_ignore, error_code):
    """Verify we detect users explicitly ignoring an error."""
    decider = style_guide.DecisionEngine(
        create_options(ignore=ignore_list, extend_ignore=extend_ignore))

    assert decider.was_ignored(error_code) is style_guide.Ignored.Explicitly


@pytest.mark.parametrize('ignore_list,extend_ignore,error_code', [
    (['E111', 'E121'], [], 'E112'),
    (['E111', 'E121'], [], 'E122'),
    (['E11', 'E12'], ['E121'], 'W121'),
    (['E2', 'E12'], [], 'E112'),
    (['E2', 'E12'], [], 'E111'),
    (['E2', 'E12'], ['W11', 'E3'], 'E111'),
])
def test_was_ignored_implicitly_selects_errors(ignore_list, extend_ignore,
                                               error_code):
    """Verify we detect users does not explicitly ignore an error."""
    decider = style_guide.DecisionEngine(
        create_options(ignore=ignore_list, extend_ignore=extend_ignore))

    assert decider.was_ignored(error_code) is style_guide.Selected.Implicitly


@pytest.mark.parametrize('select_list,enable_extensions,error_code', [
    (['E111', 'E121'], [], 'E111'),
    (['E111', 'E121'], [], 'E121'),
    (['E11', 'E12'], [], 'E121'),
    (['E2', 'E12'], [], 'E121'),
    (['E2', 'E12'], [], 'E211'),
    (['E1'], ['E2'], 'E211'),
    ([], ['E2'], 'E211'),
])
def test_was_selected_selects_errors(select_list, enable_extensions,
                                     error_code):
    """Verify we detect users explicitly selecting an error."""
    decider = style_guide.DecisionEngine(
        options=create_options(select=select_list,
                               enable_extensions=enable_extensions),
    )

    assert decider.was_selected(error_code) is style_guide.Selected.Explicitly


def test_was_selected_implicitly_selects_errors():
    """Verify we detect users implicitly selecting an error."""
    error_code = 'E121'
    decider = style_guide.DecisionEngine(
        create_options(
            select=[],
            extended_default_select=['E'],
        ),
    )

    assert decider.was_selected(error_code) is style_guide.Selected.Implicitly


@pytest.mark.parametrize('select_list,error_code', [
    (['E111', 'E121'], 'E112'),
    (['E111', 'E121'], 'E122'),
    (['E11', 'E12'], 'E132'),
    (['E2', 'E12'], 'E321'),
    (['E2', 'E12'], 'E410'),
])
def test_was_selected_excludes_errors(select_list, error_code):
    """Verify we detect users implicitly excludes an error."""
    decider = style_guide.DecisionEngine(create_options(select=select_list))

    assert decider.was_selected(error_code) is style_guide.Ignored.Implicitly


@pytest.mark.parametrize(
    'select_list,ignore_list,extend_ignore,error_code,expected', [
        (['E111', 'E121'], [], [], 'E111', style_guide.Decision.Selected),
        (['E111', 'E121'], [], [], 'E112', style_guide.Decision.Ignored),
        (['E111', 'E121'], [], [], 'E121', style_guide.Decision.Selected),
        (['E111', 'E121'], [], [], 'E122', style_guide.Decision.Ignored),
        (['E11', 'E12'], [], [], 'E132', style_guide.Decision.Ignored),
        (['E2', 'E12'], [], [], 'E321', style_guide.Decision.Ignored),
        (['E2', 'E12'], [], [], 'E410', style_guide.Decision.Ignored),
        (['E11', 'E121'], ['E1'], [], 'E112', style_guide.Decision.Selected),
        (['E11', 'E121'], [], ['E1'], 'E112', style_guide.Decision.Selected),
        (['E111', 'E121'], ['E2'], ['E3'], 'E122',
         style_guide.Decision.Ignored),
        (['E11', 'E12'], ['E13'], [], 'E132', style_guide.Decision.Ignored),
        (['E1', 'E3'], ['E32'], [], 'E321', style_guide.Decision.Ignored),
        ([], ['E2', 'E12'], [], 'E410', style_guide.Decision.Ignored),
        (['E4'], ['E2', 'E12', 'E41'], [], 'E410',
         style_guide.Decision.Ignored),
        (['E41'], ['E2', 'E12', 'E4'], [], 'E410',
         style_guide.Decision.Selected),
        (['E'], ['F'], [], 'E410', style_guide.Decision.Selected),
        (['F'], [], [], 'E410', style_guide.Decision.Ignored),
        (['E'], defaults.IGNORE, [], 'E126', style_guide.Decision.Selected),
        (['W'], defaults.IGNORE, [], 'E126', style_guide.Decision.Ignored),
        (['E'], defaults.IGNORE, [], 'W391', style_guide.Decision.Ignored),
        (['E', 'W'], ['E13'], [], 'E131', style_guide.Decision.Ignored),
        (defaults.SELECT, ['E13'], [], 'E131', style_guide.Decision.Ignored),
        (defaults.SELECT, defaults.IGNORE, ['W391'], 'E126',
         style_guide.Decision.Ignored),
        (defaults.SELECT, defaults.IGNORE, [], 'W391',
         style_guide.Decision.Selected),
    ]
)
def test_decision_for(select_list, ignore_list, extend_ignore, error_code,
                      expected):
    """Verify we decide when to report an error."""
    decider = style_guide.DecisionEngine(
        create_options(select=select_list,
                       ignore=ignore_list,
                       extend_ignore=extend_ignore))

    assert decider.decision_for(error_code) is expected


@pytest.mark.parametrize(
    'select,ignore,extend_select,enabled_extensions,error_code,expected', [
        (defaults.SELECT, [], ['I1'], [], 'I100',
            style_guide.Decision.Selected),
        (defaults.SELECT, [], ['I1'], [], 'I201',
            style_guide.Decision.Ignored),
        (defaults.SELECT, ['I2'], ['I1'], [], 'I101',
            style_guide.Decision.Selected),
        (defaults.SELECT, ['I2'], ['I1'], [], 'I201',
            style_guide.Decision.Ignored),
        (defaults.SELECT, ['I1'], ['I10'], [], 'I101',
            style_guide.Decision.Selected),
        (defaults.SELECT, ['I10'], ['I1'], [], 'I101',
            style_guide.Decision.Ignored),
        (defaults.SELECT, [], [], ['U4'], 'U401',
            style_guide.Decision.Selected),
        (defaults.SELECT, ['U401'], [], ['U4'], 'U401',
            style_guide.Decision.Ignored),
        (defaults.SELECT, ['U401'], [], ['U4'], 'U402',
            style_guide.Decision.Selected),
        (['E', 'W'], ['E13'], [], [], 'E131', style_guide.Decision.Ignored),
        (['E', 'W'], ['E13'], [], [], 'E126', style_guide.Decision.Selected),
        (['E2'], ['E21'], [], [], 'E221', style_guide.Decision.Selected),
        (['E2'], ['E21'], [], [], 'E212', style_guide.Decision.Ignored),
        (['F', 'W'], ['C90'], ['I1'], [], 'C901',
            style_guide.Decision.Ignored),
        (['E', 'W'], ['C'], [], [], 'E131',
            style_guide.Decision.Selected),
        (defaults.SELECT, defaults.IGNORE, [], ['I'], 'I101',
            style_guide.Decision.Selected),
        (defaults.SELECT, defaults.IGNORE, ['G'], ['I'], 'G101',
            style_guide.Decision.Selected),
        (defaults.SELECT, ['G1'], ['G'], ['I'], 'G101',
            style_guide.Decision.Ignored),
        (defaults.SELECT, ['E126'], [], ['I'], 'I101',
            style_guide.Decision.Selected),
        (['E', 'W'], defaults.IGNORE, ['I'], [], 'I101',
            style_guide.Decision.Ignored),
        # TODO(sigmavirus24) Figure out how to exercise the final catch-all
        # return statement
    ]
)
def test_more_specific_decision_for_logic(select, ignore, extend_select,
                                          enabled_extensions, error_code,
                                          expected):
    """Verify the logic of DecisionEngine.more_specific_decision_for."""
    decider = style_guide.DecisionEngine(
        create_options(
            select=select, ignore=ignore,
            extended_default_select=extend_select,
            enable_extensions=enabled_extensions,
        ),
    )

    assert decider.more_specific_decision_for(error_code) is expected
