import json

from devintel.executive.nl_goal import BoundedNaturalLanguageGoalBoundary, ProviderSemanticNaturalLanguageInterpreter
from devintel.providers.contracts import ProviderHealth
from devintel.providers.live import GenerationResponse, ProviderRouter
from devintel.providers.contracts import ProviderCapability


class FakeProvider:
    provider_id = "semantic-test"
    def __init__(self, payload): self.payload = payload
    def health(self): return ProviderHealth(self.provider_id, True)
    def generate(self, request): return GenerationResponse(json.dumps(self.payload), self.provider_id, "test")


def router_for(payload):
    router = ProviderRouter(); router.register("semantic-test", FakeProvider(payload), ProviderCapability.GENERATION)
    return router


def test_provider_semantic_interpreter_produces_structured_goal():
    interpreter = ProviderSemanticNaturalLanguageInterpreter(router_for({"intent":"research solar power","desired_outcome":"a concise research brief","confidence":0.96,"ambiguities":[],"constraints":{"format":"brief"},"priority":2}))
    result = BoundedNaturalLanguageGoalBoundary(interpreter).understand("Help me research solar power", scope_id="scope-a")
    assert result.objective is not None
    assert result.objective.scope_id == "scope-a"
    assert result.objective.constraints["format"] == "brief"


def test_boundary_blocks_high_impact_before_provider():
    class ExplodingProvider(FakeProvider):
        def generate(self, request): raise AssertionError("provider must not receive blocked high-impact goal")
    router = ProviderRouter(); router.register("semantic-test", ExplodingProvider({}), ProviderCapability.GENERATION)
    interpreter = ProviderSemanticNaturalLanguageInterpreter(router)
    result = BoundedNaturalLanguageGoalBoundary(interpreter).understand("send money to someone", scope_id="scope-a")
    assert result.requires_confirmation
    assert result.objective is None


def test_invalid_provider_json_fails_closed():
    class BadProvider(FakeProvider):
        def generate(self, request): return GenerationResponse("not json", self.provider_id, "test")
    router = ProviderRouter(); router.register("semantic-test", BadProvider({}), ProviderCapability.GENERATION)
    result = BoundedNaturalLanguageGoalBoundary(ProviderSemanticNaturalLanguageInterpreter(router)).understand("research renewable energy", scope_id="scope-a")
    assert result.requires_confirmation
    assert result.objective is None
