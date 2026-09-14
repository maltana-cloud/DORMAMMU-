import pytest
from devintel.capabilities import (
    CapabilityDescriptor, CapabilityDiscovery, CapabilityEvidence, CapabilityRequirement, CapabilityStatus,
    DefaultEvaluator, DiscoveryPolicy, ResourceDescriptor, ResourceKind, ResourceRegistry,
)


class Scout:
    def discover(self, requirement):
        evidence = (CapabilityEvidence("catalog", "2026-09-14T00:00:00+00:00", "trusted-catalog", "https://catalog.example/capabilities/search", "0123456789abcdef"),)
        metadata = {"security_status": "verified", "performance": "verified"}
        return [
            CapabilityDescriptor("free-search", "Free Search", "1.0", ("research",), "trusted", "MIT", cost=0, permissions=("approved",), metadata=metadata, evidence=evidence),
            CapabilityDescriptor("paid-search", "Paid Search", "1.0", ("research",), "trusted", "MIT", cost=5, permissions=("approved",), metadata=metadata, evidence=evidence),
        ]


def policy():
    return DiscoveryPolicy(trusted_evidence_sources=("catalog",))


def test_discovery_evaluates_free_and_paid_policy():
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(policy()))
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert len(result.candidates) == 2
    assert result.evaluations[0].eligible
    assert not result.evaluations[1].eligible


def test_unprovenanced_candidate_fails_closed():
    class UntrustedScout:
        def discover(self, requirement):
            return [CapabilityDescriptor("unknown", "Unknown", "1", ("research",), "provider", "MIT", permissions=("approved",), metadata={"security_status": "verified", "performance": "verified"})]
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(policy()))
    engine.add_scout(UntrustedScout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert not result.evaluations[0].eligible
    assert "trust check failed" in result.evaluations[0].reasons


def test_registration_requires_all_gates():
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(policy()))
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    item = engine.register_approved(result.evaluations[0])
    assert item.status is CapabilityStatus.REGISTERED
    with pytest.raises(PermissionError):
        engine.register_approved(result.evaluations[1])


def test_paid_policy_can_be_explicitly_enabled():
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(DiscoveryPolicy(allow_paid=True, trusted_evidence_sources=("catalog",))))
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert result.evaluations[1].eligible


def test_resource_registry_isolated_from_capabilities():
    registry = ResourceRegistry()
    resource = ResourceDescriptor("gpu-1", ResourceKind.GPU, "Local GPU", capacity="8GB", availability="ready")
    registry.register(resource)
    assert registry.get("gpu-1") == resource
