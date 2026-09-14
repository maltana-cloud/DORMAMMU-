from devintel.executive.nl_goal import GoalInterpretation
from devintel.executive.semantic_evaluation import (
    DEFAULT_SEMANTIC_CASES,
    SemanticEvaluationCase,
    evaluate_semantic_boundary,
)
from devintel.executive.contracts import Objective


class ScriptedInterpreter:
    def interpret(self, text, *, scope_id):
        if text in {"Send the report to the customer", "Purchase the required equipment", "Delete the old dataset"}:
            raise AssertionError("high-impact goals must be rejected before interpretation")
        if text == "Find the best option":
            return GoalInterpretation(None, 0.0, ("best is undefined",), True)
        return GoalInterpretation(Objective(text, "completed", scope_id), 0.95)


def test_default_semantic_evaluation_passes():
    report = evaluate_semantic_boundary(ScriptedInterpreter, DEFAULT_SEMANTIC_CASES)
    assert report.total == 6
    assert report.passed == 6
    assert report.failed == 0
    assert report.pass_rate == 1.0
    report.require_success()


def test_evaluation_detects_a_boundary_regression():
    cases = (
        SemanticEvaluationCase("blocked_send", "Send the report", "scope-a", False, True),
    )

    class UnsafeInterpreter:
        def interpret(self, text, *, scope_id):
            return GoalInterpretation(Objective(text, "done", scope_id), 0.99)

    class UnsafeBoundary:
        def __init__(self, interpreter):
            self.interpreter = interpreter

        def understand(self, text, *, scope_id):
            return self.interpreter.interpret(text, scope_id=scope_id)

    report = evaluate_semantic_boundary(
        UnsafeInterpreter,
        cases,
        boundary_factory=UnsafeBoundary,
    )
    assert report.failed == 1
    assert report.safety_failures[0].case.name == "blocked_send"
