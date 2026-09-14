import json

from devintel.executive import RoutingRequirement, SpecialistDescriptor, SpecialistKind
from devintel.providers.contracts import ProviderCapability, ProviderHealth
from devintel.providers.live import GenerationResponse
from devintel.runtime.app import DORMAMMURuntime


def test_runtime_exposes_bounded_goal_boundary_and_learned_routing():
    runtime = DORMAMMURuntime()
    try:
        class SemanticProvider:
            provider_id = "semantic-test"
            def health(self): return ProviderHealth(self.provider_id, True)
            def generate(self, request):
                return GenerationResponse(json.dumps({"intent":"research solar power","desired_outcome":"brief","confidence":0.96,"ambiguities":[],"constraints":{},"priority":1}), self.provider_id, "test")

        runtime.register_generation_provider("semantic-test", SemanticProvider(), priority=2000)
        goal = runtime.understand_goal("Research solar power", scope_id="scope-a")
        assert goal.objective is not None
        assert goal.objective.scope_id == "scope-a"

        runtime.specialist_router.register(SpecialistDescriptor("s1", SpecialistKind.SPECIALIST, "local", "1", ("research",), 0.1, {}, True, True))
        selected = runtime.route_specialist("scope-a", RoutingRequirement("research", ("research",)))
        assert selected.specialist.specialist_id == "s1"
    finally:
        runtime.close()


def test_runtime_high_impact_goal_fails_closed_before_provider():
    runtime = DORMAMMURuntime()
    try:
        result = runtime.understand_goal("send money to someone", scope_id="scope-a")
        assert result.objective is None
        assert result.requires_confirmation
    finally:
        runtime.close()
