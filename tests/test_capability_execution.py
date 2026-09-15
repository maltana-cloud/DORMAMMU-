from devintel.providers import (
    CapabilityExecutor,
    GenerationRequest,
    GenerationResponse,
    ProviderCapability,
    ProviderHealth,
    ProviderRouter,
    ResearchRequest,
    ResearchResult,
)


class GoodGeneration:
    provider_id = "good-gen"

    def health(self):
        return ProviderHealth(self.provider_id, True)

    def generate(self, request):
        return GenerationResponse("hello", self.provider_id, model="test-model")


class GoodResearch:
    provider_id = "good-research"

    def health(self):
        return ProviderHealth(self.provider_id, True)

    def search(self, request):
        return (ResearchResult("https://example.com", "Example", "content", self.provider_id),)


def test_executor_exposes_generation_as_capability_result():
    router = ProviderRouter()
    router.register("good-gen", GoodGeneration(), ProviderCapability.GENERATION)
    execution = CapabilityExecutor(router).generate(GenerationRequest("hello"))
    assert execution.capability is ProviderCapability.GENERATION
    assert execution.result.success
    assert execution.result.provider_id == "good-gen"
    assert execution.attempted == ("good-gen",)


def test_executor_exposes_research_as_capability_result():
    router = ProviderRouter()
    router.register("good-research", GoodResearch(), ProviderCapability.RESEARCH)
    execution = CapabilityExecutor(router).research(ResearchRequest("DORMAMMU"))
    assert execution.capability is ProviderCapability.RESEARCH
    assert execution.result.success
    assert execution.result.output[0].source == "good-research"


def test_executor_rejects_invalid_attempt_limit():
    router = ProviderRouter()
    try:
        CapabilityExecutor(router, max_attempts=0)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
