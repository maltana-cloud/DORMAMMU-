import json

from devintel.executive.nl_goal import (
    BoundedNaturalLanguageGoalBoundary,
    GoalInterpretation,
    ProviderSemanticNaturalLanguageInterpreter,
)
from devintel.providers.contracts import ProviderCapability, ProviderHealth
from devintel.providers.live import GenerationResponse, ProviderRouter


class FakeProvider:
    provider_id = "fake"

    def __init__(self, payload=None, *, error=False):
        self.payload = payload
        self.error = error

    def generate(self, request):
        if self.error:
            raise RuntimeError("offline")
        return GenerationResponse(json.dumps(self.payload), self.provider_id)

    def health(self):
        return ProviderHealth(self.provider_id, True)


def interpreter(payload, *, error=False):
    router = ProviderRouter()
    router.register("fake", FakeProvider(payload, error=error), ProviderCapability.GENERATION)
    return ProviderSemanticNaturalLanguageInterpreter(router)


def valid_payload():
    return {"intent": "research", "desired_outcome": "report", "confidence": 0.99,
            "ambiguities": [], "constraints": {}, "priority": 0}


def test_provider_schema_requires_exact_fields():
    payload = {**valid_payload(), "authority": "admin"}
    result = interpreter(payload).interpret("research", scope_id="scope")
    assert result.objective is None
    assert result.requires_confirmation


def test_non_finite_confidence_fails_closed():
    payload = {**valid_payload(), "confidence": float("nan")}
    result = interpreter(payload).interpret("research", scope_id="scope")
    assert result.objective is None
    assert result.requires_confirmation


def test_oversized_semantic_field_fails_closed():
    payload = {**valid_payload(), "intent": "x" * 2049}
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


def test_provider_exception_becomes_confirmation_required():
    result = interpreter(valid_payload(), error=True).interpret("research", scope_id="scope")
    assert isinstance(result, GoalInterpretation)
    assert result.objective is None
    assert result.requires_confirmation


def test_action_like_provider_output_remains_only_an_objective():
    payload = {**valid_payload(), "intent": "delete the database", "desired_outcome": "database deleted"}
    result = interpreter(payload).interpret("research", scope_id="scope")
    assert result.objective is not None
    assert result.objective.scope_id == "scope"
    assert not hasattr(result.objective, "authority")
