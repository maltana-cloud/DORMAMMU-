from devintel.capabilities import ResourceManager, ResourceRequest, ResourceRegistry
from devintel.capabilities.contracts import ResourceDescriptor, ResourceKind
from devintel.capabilities.leases import ResourceLeaseStore
from devintel.modules.research import EvidenceAcquisitionGateway, InMemoryResearchStore
from devintel.providers.contracts import ProviderCapability, ProviderHealth
from devintel.providers.live import ProviderRouter, ResearchRequest, ResearchResult
from devintel.providers.resource_execution import ResourceAwareProviderExecutor


class ResearchProvider:
    provider_id = "test-research"

    def health(self):
        return ProviderHealth(self.provider_id, True)

    def search(self, request: ResearchRequest):
        return (ResearchResult("https://example.com/source", "Source", "verified later", "example"),)


class FailingProvider:
    provider_id = "bad"

    def health(self):
        return ProviderHealth(self.provider_id, True)

    def search(self, request):
        raise RuntimeError("failure")


def resources():
    registry = ResourceRegistry()
    registry.register(ResourceDescriptor("api-1", ResourceKind.API, "test api", capacity="1", availability="ready", permissions=("approved",)))
    leases = ResourceLeaseStore()
    return ResourceManager(registry, leases)


def test_evidence_gateway_acquires_untrusted_documents_without_verifying_them():
    router = ProviderRouter()
    router.register("test-research", ResearchProvider(), ProviderCapability.RESEARCH, priority=1)
    store = InMemoryResearchStore()
    gateway = EvidenceAcquisitionGateway(router, store)
    result = gateway.acquire("dormammu", max_results=3)
    assert result.accepted == 1
    assert result.provider_id == "test-research"
    assert store.count_documents() == 1
    assert store.count_observations() == 0


def test_evidence_gateway_rejects_empty_provider_content_and_bounds_results():
    class EmptyProvider(ResearchProvider):
        provider_id = "empty"
        def search(self, request):
            return tuple(ResearchResult(f"https://example.com/{i}", "x", "", "x") for i in range(10))

    router = ProviderRouter()
    router.register("empty", EmptyProvider(), ProviderCapability.RESEARCH)
    gateway = EvidenceAcquisitionGateway(router)
    result = gateway.acquire("query", max_results=2)
    assert result.accepted == 0
    assert result.rejected == 2


def test_resource_aware_provider_executor_releases_lease_on_success():
    router = ProviderRouter()
    router.register("test-research", ResearchProvider(), ProviderCapability.RESEARCH)
    manager = resources()
    executor = ResourceAwareProviderExecutor(router, manager)
    result = executor.research(ResearchRequest("query"))
    assert result.result.success
    assert result.resource_id == "api-1"
    assert result.reservation_id
    assert manager.active_reservations() == ()
    manager.close()


def test_resource_aware_provider_executor_fails_closed_without_capacity():
    router = ProviderRouter()
    router.register("test-research", ResearchProvider(), ProviderCapability.RESEARCH)
    registry = ResourceRegistry()
    manager = ResourceManager(registry, ResourceLeaseStore())
    result = ResourceAwareProviderExecutor(router, manager).research(ResearchRequest("query"))
    assert not result.result.success
    assert result.resource_id is None
    assert manager.active_reservations() == ()
    manager.close()


def test_provider_failure_is_fallback_capable_and_lease_is_cleaned():
    class Good(ResearchProvider):
        provider_id = "good"

    router = ProviderRouter(max_attempts=2)
    router.register("bad", FailingProvider(), ProviderCapability.RESEARCH, priority=1)
    router.register("good", Good(), ProviderCapability.RESEARCH, priority=2)
    manager = resources()
    result = ResourceAwareProviderExecutor(router, manager).research(ResearchRequest("query"))
    assert result.result.success
    assert result.result.provider_id == "good"
    assert manager.active_reservations() == ()
    manager.close()
