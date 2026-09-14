from devintel.capabilities import (
    CapabilityDescriptor,
    CapabilityEvidence,
    CapabilityResourceDiscoveryEngine,
    CapabilityResourceScheduler,
    CapabilityStatus,
    DiscoveryPolicy,
    ResourceDescriptor,
    ResourceKind,
)
from devintel.capabilities.registry import CapabilityRegistry, ResourceRegistry
from devintel.capabilities.contracts import CapabilityRequirement


def _capability(capability_id: str, cost: float = 0.0) -> CapabilityDescriptor:
    return CapabilityDescriptor(
        capability_id=capability_id,
        name=capability_id,
        version="1",
        interfaces=("inference",),
        provider="trusted-provider",
        license="Apache-2.0",
        status=CapabilityStatus.DISCOVERED,
        cost=cost,
        permissions=("approved",),
        metadata={"performance": "good", "security_status": "safe"},
        evidence=(CapabilityEvidence("catalog", "trusted-provider", True, "https://example.com/evidence"),),
    )


def _engine() -> CapabilityResourceDiscoveryEngine:
    capabilities = CapabilityRegistry()
    capabilities.register(_capability("model-a", 0.0))
    capabilities.register(_capability("model-b", 0.0))
    resources = ResourceRegistry()
    resources.register(ResourceDescriptor("gpu-a", ResourceKind.GPU, "GPU A", capacity="1", availability="ready", permissions=("approved",)))
    return CapabilityResourceDiscoveryEngine(
        capability_registry=capabilities,
        resource_registry=resources,
        discovery_policy=DiscoveryPolicy(
            trusted_evidence_sources=("catalog",),
            require_provenance=True,
        ),
    )


def test_scheduler_selects_eligible_capability_and_reserves_resource():
    engine = _engine()
    engine.discovery.add_scout(type("Scout", (), {"discover": lambda self, requirement: tuple(engine.capability_registry.get(x) for x in ("model-a", "model-b"))})())
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert plan.granted
    assert plan.selected_capability_id == "model-a"
    assert plan.selected_resource_id == "gpu-a"
    scheduler.release(plan)
    engine.close()


def test_scheduler_fails_closed_when_resource_capacity_is_unavailable():
    engine = _engine()
    engine.discovery.add_scout(type("Scout", (), {"discover": lambda self, requirement: (engine.capability_registry.get("model-a"),)})())
    engine.reserve_resource(ResourceKind.GPU)
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert not plan.granted
    assert plan.selected_capability_id is None
    engine.close()


def test_scheduler_rejects_unapproved_capability_without_reserving_resource():
    engine = _engine()
    unapproved = _capability("model-unapproved")
    unapproved = CapabilityDescriptor(
        capability_id=unapproved.capability_id, name=unapproved.name, version=unapproved.version,
        interfaces=unapproved.interfaces, provider=unapproved.provider, license=unapproved.license,
        permissions=(), metadata=unapproved.metadata, evidence=unapproved.evidence,
    )
    engine.capability_registry.register(unapproved)
    engine.discovery.add_scout(type("Scout", (), {"discover": lambda self, requirement: (unapproved,)})())
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert not plan.granted
    assert engine.resource_manager.active_reservations() == ()
    engine.close()
