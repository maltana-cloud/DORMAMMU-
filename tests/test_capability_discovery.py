import pytest
from devintel.capabilities import (
    CapabilityDescriptor, CapabilityDiscovery, CapabilityEvidence, CapabilityRequirement, CapabilityStatus,
    DefaultEvaluator, DiscoveryPolicy, ResourceDescriptor, ResourceKind, ResourceRegistry,
    CapabilityResourceDiscoveryEngine, CapabilityLifecycle, LifecycleStore,
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
    assert result.best is result.evaluations[0]


def test_unprovenanced_candidate_fails_closed():
    class UntrustedScout:
        def discover(self, requirement):
            return [CapabilityDescriptor("unknown", "Unknown", "1", ("research",), "provider", "MIT", permissions=("approved",), metadata={"security_status": "verified", "performance": "verified"})]
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(policy()))
    engine.add_scout(UntrustedScout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert not result.evaluations[0].eligible
    assert "trust check failed" in result.evaluations[0].reasons


def test_scout_failure_is_isolated():
    class BrokenScout:
        def discover(self, requirement):
            raise RuntimeError("provider unavailable")
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(policy()))
    engine.add_scout(BrokenScout())
    engine.add_scout(Scout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert len(result.candidates) == 2
    assert result.scout_failures == ("scout:0:RuntimeError",)


def test_discovery_uses_configured_minimum_score():
    class PartiallyValidScout:
        def discover(self, requirement):
            evidence = (CapabilityEvidence("catalog", "2026-09-14T00:00:00+00:00", "trusted-catalog", "https://catalog.example/capabilities/search", "0123456789abcdef"),)
            return [CapabilityDescriptor("partial", "Partial", "1", ("research",), "trusted", "MIT", permissions=("approved",), metadata={"performance": "poor"}, evidence=evidence)]
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(DiscoveryPolicy(minimum_score=0.9, trusted_evidence_sources=("catalog",))))
    engine.add_scout(PartiallyValidScout())
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert result.best is None
    assert "minimum score check failed" in result.evaluations[0].reasons


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


def test_engine_admission_requires_owner_approval_and_records_lifecycle():
    lifecycle_store = LifecycleStore()
    engine = CapabilityResourceDiscoveryEngine(
        discovery_policy=policy(),
        lifecycle_store=lifecycle_store,
    )
    engine.discovery.add_scout(Scout())
    plan = engine.plan_acquisition(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert plan.ready_for_approval
    with pytest.raises(PermissionError):
        engine.approve_and_register(plan)
    registered = engine.approve_and_register(plan, owner_approved=True)
    assert registered.status is CapabilityStatus.REGISTERED
    history = lifecycle_store.history("free-search")
    assert [event.to_status for event in history] == [CapabilityStatus.EVALUATED, CapabilityStatus.APPROVED, CapabilityStatus.REGISTERED]
    engine.close()


def test_engine_canary_activation_and_fallback_are_explicit():
    engine = CapabilityResourceDiscoveryEngine(discovery_policy=policy())
    engine.discovery.add_scout(Scout())
    plan = engine.plan_acquisition(CapabilityRequirement("research.search", "find sources", ("research",)))
    engine.approve_and_register(plan, owner_approved=True)
    engine.enter_canary("free-search")
    decision = engine.evaluate_canary("free-search", __import__("devintel.capabilities", fromlist=["CanaryHealth"]).CanaryHealth(True, 1.0, 0.0, 10.0))
    assert decision.activated
    fallback = engine.fallback(plan, "free-search")
    assert fallback is None
    engine.close()
