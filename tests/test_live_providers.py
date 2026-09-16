from devintel.providers import (
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


class BrokenGeneration:
    provider_id = "broken-gen"
    def health(self):
        return ProviderHealth(self.provider_id, True)
    def generate(self, request):
        raise RuntimeError("quota exhausted")


class MismatchedGeneration:
    provider_id = "mismatch-gen"
    def health(self):
        return ProviderHealth(self.provider_id, True)
    def generate(self, request):
        return GenerationResponse("spoofed", "other-provider")


class GoodResearch:
    provider_id = "good-research"
    def health(self):
        return ProviderHealth(self.provider_id, True)
    def search(self, request):
        return (ResearchResult("https://example.com", "Example", "content", self.provider_id),)


class BadResearch:
    provider_id = "bad-research"
    def health(self):
        return ProviderHealth(self.provider_id, True)
    def search(self, request):
        return (object(),)


def test_generation_falls_back_after_provider_failure():
    router = ProviderRouter()
    router.register("broken-gen", BrokenGeneration(), ProviderCapability.GENERATION, priority=1)
    router.register("good-gen", GoodGeneration(), ProviderCapability.GENERATION, priority=2)
    result = router.generate(GenerationRequest("say hello"))
    assert result.success
    assert result.provider_id == "good-gen"
    assert router.status(ProviderCapability.GENERATION)[0][3] == 1


def test_research_falls_back_on_invalid_provider_output():
    router = ProviderRouter()
    router.register("bad-research", BadResearch(), ProviderCapability.RESEARCH, priority=1)
    router.register("good-research", GoodResearch(), ProviderCapability.RESEARCH, priority=2)
    result = router.research(ResearchRequest("DEVINTEL"))
    assert result.success
    assert result.provider_id == "good-research"
    assert result.output[0].url == "https://example.com"


def test_unavailable_provider_fails_closed():
    router = ProviderRouter()
    result = router.generate(GenerationRequest("hello"))
    assert not result.success
    assert result.error == "no generation provider available"


def test_disabled_provider_is_skipped():
    router = ProviderRouter()
    router.register("good-gen", GoodGeneration(), ProviderCapability.GENERATION)
    assert router.disable(ProviderCapability.GENERATION, "good-gen")
    result = router.generate(GenerationRequest("hello"))
    assert not result.success


def test_provider_identity_must_match_registration():
    router = ProviderRouter()
    class WrongId:
        provider_id = "actual"
        def health(self): return ProviderHealth(self.provider_id, True)
        def generate(self, request): return GenerationResponse("x", self.provider_id)
    import pytest
    with pytest.raises(ValueError):
        router.register("declared", WrongId(), ProviderCapability.GENERATION)


def test_generation_rejects_output_identity_spoofing_and_falls_back():
    router = ProviderRouter()
    router.register("mismatch-gen", MismatchedGeneration(), ProviderCapability.GENERATION, priority=1)
    router.register("good-gen", GoodGeneration(), ProviderCapability.GENERATION, priority=2)
    result = router.generate(GenerationRequest("hello"))
    assert result.success
    assert result.provider_id == "good-gen"
    assert router.status(ProviderCapability.GENERATION)[0][3] == 1


def test_router_bounds_fallback_attempts():
    router = ProviderRouter(max_attempts=1)
    router.register("broken-gen", BrokenGeneration(), ProviderCapability.GENERATION, priority=1)
    router.register("good-gen", GoodGeneration(), ProviderCapability.GENERATION, priority=2)
    result = router.generate(GenerationRequest("hello"))
    assert not result.success
    assert router.status(ProviderCapability.GENERATION)[0][3] == 1
    assert router.status(ProviderCapability.GENERATION)[1][3] == 0
