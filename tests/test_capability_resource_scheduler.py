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
        capability_id=capability_id, name=capability_id, version="1",
        interfaces=("inference",), provider="trusted-provider", license="Apache-2.0",
        status=CapabilityStatus.DISCOVERED, cost=cost, permissions=("approved",),
        metadata={"performance": "good", "security_status": "safe"},
        evidence=(CapabilityEvidence(
            "catalog", "2026-09-14T00:00:00+00:00", "trusted-provider",
            "https://example.com/evidence", "0123456789abcdef",
        ),),
    )


def _engine() -> CapabilityResourceDiscoveryEngine:
    capabilities = CapabilityRegistry()
    capabilities.register(_capability("model-a", 0.0))
    capabilities.register(_capability("model-b", 0.0))
    resources = ResourceRegistry()
    resources.register(ResourceDescriptor(
        "gpu-a", ResourceKind.GPU, "GPU A", capacity="1", availability="ready",
        permissions=("approved",),
    ))
    return CapabilityResourceDiscoveryEngine(
        capability_registry=capabilities, resource_registry=resources,
        discovery_policy=DiscoveryPolicy(trusted_evidence_sources=("catalog",), require_provenance=True),
    )


def _scout(engine, ids):
    class Scout:
        def discover(self, requirement):
            return tuple(engine.capability_registry.get(item) for item in ids)
    return Scout()


def test_scheduler_selects_eligible_capability_and_confirms_resource_without_reserving():
    engine = _engine()
    engine.discovery.add_scout(_scout(engine, ("model-a", "model-b")))
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert plan.granted
    assert plan.resource_kind is ResourceKind.GPU
    assert plan.selected_capability_id == "model-a"
    assert plan.selected_resource_id == "gpu-a"
    assert plan.reservation_id is None
    assert engine.resource_manager.active_reservations() == ()
    admitted = scheduler.admit(plan)
    assert admitted.reservation_id
    scheduler.release(admitted)
    engine.close()


def test_scheduler_fails_closed_when_resource_capacity_is_unavailable():
    engine = _engine()
    engine.discovery.add_scout(_scout(engine, ("model-a",)))
    existing = engine.reserve_resource(ResourceKind.GPU)
    assert existing.granted
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert not plan.granted
    assert plan.selected_capability_id is None
    engine.release_resource(existing.reservation_id)
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
    engine.discovery.add_scout(_scout(engine, ("model-unapproved",)))
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert not plan.granted
    assert engine.resource_manager.active_reservations() == ()
    engine.close()


def test_scheduler_does_not_reserve_wrong_resource_kind_during_admission():
    engine = _engine()
    engine.discovery.add_scout(_scout(engine, ("model-a",)))
    scheduler = CapabilityResourceScheduler(engine)
    plan = scheduler.plan(CapabilityRequirement("inference", "run inference", ("inference",)), resource_kind=ResourceKind.GPU)
    assert plan.granted
    bad_plan = plan.__class__(
        plan.requirement, ResourceKind.CPU, plan.selected_capability_id,
        plan.selected_resource_id, None, plan.attempts, plan.reason,
    )
    try:
        scheduler.admit(bad_plan)
    except RuntimeError as exc:
        assert "resource changed" in str(exc)
    else:
        raise AssertionError("mismatched resource kind must fail closed")
    assert engine.resource_manager.active_reservations() == ()
    engine.close()
