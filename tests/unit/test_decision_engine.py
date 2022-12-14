"""Tests for the flake8.style_guide.DecisionEngine class."""
from __future__ import annotations

import argparse

import pytest

from flake8 import style_guide


def create_options(**kwargs):
    """Create and return an instance of argparse.Namespace."""
    kwargs.setdefault("select", None)
    kwargs.setdefault("ignore", None)
    kwargs.setdefault("extend_select", None)
    kwargs.setdefault("extend_ignore", None)
    kwargs.setdefault("extended_default_select", ["C90", "F", "E", "W"])
    kwargs.setdefault("extended_default_ignore", [])
    kwargs.setdefault("disable_noqa", False)
    return argparse.Namespace(**kwargs)


@pytest.mark.parametrize(
    "ignore_list,extend_ignore,error_code",
    [
        (["E111", "E121"], [], "E111"),
        (["E111", "E121"], [], "E121"),
        (["E111"], ["E121"], "E121"),
        (["E11", "E12"], [], "E121"),
        (["E2", "E12"], [], "E121"),
        (["E2", "E12"], [], "E211"),
        (["E2", "E3"], ["E12"], "E211"),
    ],
)
def test_was_ignored_ignores_errors(ignore_list, extend_ignore, error_code):
    """Verify we detect users explicitly ignoring an error."""
    decider = style_guide.DecisionEngine(
        create_options(ignore=ignore_list, extend_ignore=extend_ignore)
    )

    assert decider.was_ignored(error_code) is style_guide.Ignored.Explicitly


@pytest.mark.parametrize(
    "ignore_list,extend_ignore,error_code",
    [
        (["E111", "E121"], [], "E112"),
        (["E111", "E121"], [], "E122"),
        (["E11", "E12"], ["E121"], "W121"),
        (["E2", "E12"], [], "E112"),
        (["E2", "E12"], [], "E111"),
        (["E2", "E12"], ["W11", "E3"], "E111"),
    ],
)
def test_was_ignored_implicitly_selects_errors(
    ignore_list, extend_ignore, error_code
):
    """Verify we detect users does not explicitly ignore an error."""
    decider = style_guide.DecisionEngine(
        create_options(ignore=ignore_list, extend_ignore=extend_ignore)
    )

    assert decider.was_ignored(error_code) is style_guide.Selected.Implicitly


@pytest.mark.parametrize(
    ("select_list", "extend_select", "error_code"),
    (
        (["E111", "E121"], [], "E111"),
        (["E111", "E121"], [], "E121"),
        (["E11", "E12"], [], "E121"),
        (["E2", "E12"], [], "E121"),
        (["E2", "E12"], [], "E211"),
        (["E1"], ["E2"], "E211"),
        ([], ["E2"], "E211"),
        (["E1"], ["E2"], "E211"),
        (["E111"], ["E121"], "E121"),
    ),
)
def test_was_selected_selects_errors(select_list, extend_select, error_code):
    """Verify we detect users explicitly selecting an error."""
    decider = style_guide.DecisionEngine(
        options=create_options(
            select=select_list,
            extend_select=extend_select,
        ),
    )

    assert decider.was_selected(error_code) is style_guide.Selected.Explicitly


def test_was_selected_implicitly_selects_errors():
    """Verify we detect users implicitly selecting an error."""
    error_code = "E121"
    decider = style_guide.DecisionEngine(
        create_options(
            select=None,
            extended_default_select=["E"],
        ),
    )

    assert decider.was_selected(error_code) is style_guide.Selected.Implicitly


@pytest.mark.parametrize(
    "select_list,error_code",
    [
        (["E111", "E121"], "E112"),
        (["E111", "E121"], "E122"),
        (["E11", "E12"], "E132"),
        (["E2", "E12"], "E321"),
        (["E2", "E12"], "E410"),
    ],
)
def test_was_selected_excludes_errors(select_list, error_code):
    """Verify we detect users implicitly excludes an error."""
    decider = style_guide.DecisionEngine(create_options(select=select_list))

    assert decider.was_selected(error_code) is style_guide.Ignored.Implicitly


@pytest.mark.parametrize(
    "select_list,ignore_list,extend_ignore,error_code,expected",
    [
        (["E111", "E121"], [], None, "E111", style_guide.Decision.Selected),
        (["E111", "E121"], [], None, "E112", style_guide.Decision.Ignored),
        (["E111", "E121"], [], None, "E121", style_guide.Decision.Selected),
        (["E111", "E121"], [], None, "E122", style_guide.Decision.Ignored),
        (["E11", "E12"], [], None, "E132", style_guide.Decision.Ignored),
        (["E2", "E12"], [], None, "E321", style_guide.Decision.Ignored),
        (["E2", "E12"], [], None, "E410", style_guide.Decision.Ignored),
        (["E11", "E121"], ["E1"], [], "E112", style_guide.Decision.Selected),
        (["E11", "E121"], [], ["E1"], "E112", style_guide.Decision.Selected),
        (
            ["E111", "E121"],
            ["E2"],
            ["E3"],
            "E122",
            style_guide.Decision.Ignored,
        ),
        (["E11", "E12"], ["E13"], None, "E132", style_guide.Decision.Ignored),
        (["E1", "E3"], ["E32"], None, "E321", style_guide.Decision.Ignored),
        ([], ["E2", "E12"], None, "E410", style_guide.Decision.Ignored),
        (
            ["E4"],
            ["E2", "E12", "E41"],
            None,
            "E410",
            style_guide.Decision.Ignored,
        ),
        (
            ["E41"],
            ["E2", "E12", "E4"],
            None,
            "E410",
            style_guide.Decision.Selected,
        ),
        (["E"], ["F"], None, "E410", style_guide.Decision.Selected),
        (["F"], [], None, "E410", style_guide.Decision.Ignored),
        (["E"], None, None, "E126", style_guide.Decision.Selected),
        (["W"], None, None, "E126", style_guide.Decision.Ignored),
        (["E"], None, None, "W391", style_guide.Decision.Ignored),
        (["E", "W"], ["E13"], None, "E131", style_guide.Decision.Ignored),
        (None, ["E13"], None, "E131", style_guide.Decision.Ignored),
        (
            None,
            None,
            ["W391"],
            "E126",
            style_guide.Decision.Ignored,
        ),
        (
            None,
            None,
            None,
            "W391",
            style_guide.Decision.Selected,
        ),
    ],
)
def test_decision_for(
    select_list, ignore_list, extend_ignore, error_code, expected
):
    """Verify we decide when to report an error."""
    decider = style_guide.DecisionEngine(
        create_options(
            select=select_list,
            ignore=ignore_list,
            extend_ignore=extend_ignore,
        )
    )

    assert decider.decision_for(error_code) is expected


def test_implicitly_selected_and_implicitly_ignored_defers_to_length():
    decider = style_guide.DecisionEngine(
        create_options(
            # no options selected by user
            select=None,
            ignore=None,
            extend_select=None,
            extend_ignore=None,
            # a plugin is installed and extends default ignore
            extended_default_select=["P"],
            extended_default_ignore=["P002"],
        ),
    )

    assert decider.decision_for("P001") is style_guide.Decision.Selected
    assert decider.decision_for("P002") is style_guide.Decision.Ignored


def test_user_can_extend_select_to_enable_plugin_default_ignored():
    decider = style_guide.DecisionEngine(
        create_options(
            # user options --extend-select=P002
            select=None,
            ignore=None,
            extend_select=["P002"],
            extend_ignore=None,
            # a plugin is installed and extends default ignore
            extended_default_select=["P"],
            extended_default_ignore=["P002"],
        ),
    )

    assert decider.decision_for("P002") is style_guide.Decision.Selected


def test_plugin_extends_default_ignore_but_extend_selected():
    decider = style_guide.DecisionEngine(
        create_options(
            # user options --extend-select P002 --extend-ignore E501
            select=None,
            ignore=None,
            extend_select=["P002"],
            extend_ignore=["E501"],
            # a plugin is installed and extends default ignore
            extended_default_select=["P"],
            extended_default_ignore=["P002"],
        ),
    )

    assert decider.decision_for("P002") is style_guide.Decision.Selected
