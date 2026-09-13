import pytest
from devintel.capabilities import (
    CapabilityDescriptor, CapabilityDiscovery, CapabilityRequirement, CapabilityStatus,
    DefaultEvaluator, DiscoveryPolicy, ResourceDescriptor, ResourceKind, ResourceRegistry,
)


class Scout:
    def discover(self, requirement):
        return [
            CapabilityDescriptor("free-search", "Free Search", "1.0", ("research",), "trusted", "MIT", cost=0, permissions=("approved",)),
            CapabilityDescriptor("paid-search", "Paid Search", "1.0", ("research",), "trusted", "MIT", cost=5, permissions=("approved",)),
        ]


def test_discovery_evaluates_free_and_paid_policy():
    engine = CapabilityDiscovery()
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert len(result.candidates) == 2
    assert result.evaluations[0].eligible
    assert not result.evaluations[1].eligible


def test_registration_requires_all_gates():
    engine = CapabilityDiscovery()
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    item = engine.register_approved(result.evaluations[0])
    assert item.status is CapabilityStatus.REGISTERED
    with pytest.raises(PermissionError):
        engine.register_approved(result.evaluations[1])


def test_paid_policy_can_be_explicitly_enabled():
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(DiscoveryPolicy(allow_paid=True)))
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert result.evaluations[1].eligible


def test_resource_registry_isolated_from_capabilities():
    registry = ResourceRegistry()
    resource = ResourceDescriptor("gpu-1", ResourceKind.GPU, "Local GPU", capacity="8GB", availability="ready")
    registry.register(resource)
    assert registry.get("gpu-1") == resource
