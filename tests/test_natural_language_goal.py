import pytest
from devintel.executive.nl_goal import (
    BoundedNaturalLanguageGoalBoundary,
    DeterministicNaturalLanguageInterpreter,
    GoalInterpretation,
)
from devintel.executive.contracts import Objective


def test_simple_goal_is_normalized_with_matching_scope():
    result = BoundedNaturalLanguageGoalBoundary(DeterministicNaturalLanguageInterpreter()).understand(
        "Research renewable energy storage", scope_id="scope-a"
    )
    assert result.objective is not None
    assert result.objective.scope_id == "scope-a"
    assert result.confidence >= .85
    assert not result.requires_confirmation


def test_high_impact_goal_fails_closed():
    result = BoundedNaturalLanguageGoalBoundary(DeterministicNaturalLanguageInterpreter()).understand(
        "publish the report", scope_id="scope-a"
    )
    assert result.objective is None
    assert result.requires_confirmation


def test_low_confidence_requires_confirmation():
    class Ambiguous:
        def interpret(self, text, *, scope_id):
            return GoalInterpretation(Objective("x", "y", scope_id), .5, ("ambiguous",), False)
    result = BoundedNaturalLanguageGoalBoundary(Ambiguous()).understand("do something", scope_id="scope-a")
    assert result.requires_confirmation


def test_interpreter_cannot_change_scope():
    class WrongScope:
        def interpret(self, text, *, scope_id):
            return GoalInterpretation(Objective("x", "y", "other"), .99)
    with pytest.raises(ValueError):
        BoundedNaturalLanguageGoalBoundary(WrongScope()).understand("do useful research", scope_id="scope-a")
