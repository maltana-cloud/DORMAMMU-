import json

from devintel.executive.nl_goal import (
    BoundedNaturalLanguageGoalBoundary,
    GoalInterpretation,
    ProviderSemanticNaturalLanguageInterpreter,
)
from devintel.providers.live import ProviderResult, ProviderRouter


class FakeProvider:
    def __init__(self, payload):
        self.payload = payload

    def generate(self, request):
        return ProviderResult(True, type("Output", (), {"text": json.dumps(self.payload)})(), "")


def interpreter(payload):
    router = ProviderRouter()
    router.register("fake", FakeProvider(payload))
    return ProviderSemanticNaturalLanguageInterpreter(router)


def test_provider_schema_requires_exact_fields():
    payload = {"intent": "research", "desired_outcome": "report", "confidence": 0.99,
               "ambiguities": [], "constraints": {}, "priority": 0, "authority": "admin"}
    result = interpreter(payload).interpret("research", scope_id="scope")
    assert result.objective is None
    assert result.requires_confirmation


def test_non_finite_confidence_fails_closed():
    payload = {"intent": "research", "desired_outcome": "report", "confidence": float("nan"),
               "ambiguities": [], "constraints": {}, "priority": 0}
    result = interpreter(payload).interpret("research", scope_id="scope")
    assert result.objective is None
    assert result.requires_confirmation


def test_oversized_semantic_field_fails_closed():
    payload = {"intent": "x" * 2049, "desired_outcome": "report", "confidence": 0.99,
               "ambiguities": [], "constraints": {}, "priority": 0}
    result = interpreter(payload).interpret("research", scope_id="scope")
    assert result.objective is None


def test_high_impact_goal_is_blocked_before_provider():
    class ExplodingInterpreter:
        def interpret(self, text, *, scope_id):
            raise AssertionError("provider must not receive high-impact goal")

    result = BoundedNaturalLanguageGoalBoundary(ExplodingInterpreter()).understand(
        "send the report", scope_id="scope"
    )
    assert result.objective is None
    assert result.requires_confirmation


def test_scope_mismatch_is_fail_closed():
    payload = {"intent": "research", "desired_outcome": "report", "confidence": 0.99,
               "ambiguities": [], "constraints": {}, "priority": 0}
    boundary = BoundedNaturalLanguageGoalBoundary(interpreter(payload))
    result = boundary.understand("research", scope_id="scope-a")
    assert result.objective is not None
    assert result.objective.scope_id == "scope-a"


def test_provider_exception_becomes_confirmation_required():
    class BrokenProvider:
        def generate(self, request):
            raise RuntimeError("offline")

    router = ProviderRouter()
    router.register("broken", BrokenProvider())
    result = ProviderSemanticNaturalLanguageInterpreter(router).interpret("research", scope_id="scope")
    assert isinstance(result, GoalInterpretation)
    assert result.objective is None
    assert result.requires_confirmation
