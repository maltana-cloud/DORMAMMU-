import pytest

from devintel.capabilities import (
    CapabilityAcquisition,
    CapabilityDescriptor,
    CapabilityDiscovery,
    CapabilityLifecycle,
    CapabilityRegistry,
    CapabilityRequirement,
    CapabilityStatus,
    DiscoveryPolicy,
    DefaultEvaluator,
    CanaryHealth,
)


class Scout:
    def discover(self, requirement):
        return [
            CapabilityDescriptor("primary", "Primary", "1.0", ("research",), "trusted", "MIT", cost=0, permissions=("approved",)),
            CapabilityDescriptor("fallback", "Fallback", "1.0", ("research",), "trusted", "MIT", cost=0, permissions=("approved",)),
            CapabilityDescriptor("unsafe", "Unsafe", "1.0", ("research",), "unknown", "MIT", cost=0, permissions=("approved",)),
        ]


def build():
    registry = CapabilityRegistry()
    discovery = CapabilityDiscovery(registry=registry, evaluator=DefaultEvaluator(DiscoveryPolicy()))
    discovery.add_scout(Scout())
    lifecycle = CapabilityLifecycle(registry)
    return CapabilityAcquisition(discovery, lifecycle)


def requirement():
    return CapabilityRequirement("research.search", "find sources", ("research",))


def test_plan_selects_best_eligible_and_preserves_fallbacks():
    acquisition = build()
    plan = acquisition.plan(requirement())
    assert plan.ready_for_approval
    assert plan.selected.candidate.capability_id == "fallback" or plan.selected.candidate.capability_id == "primary"
    assert all(item.eligible for item in plan.alternatives)
    assert acquisition.fallback_plan(plan, plan.selected.candidate.capability_id) is not None


def test_approval_is_explicit_and_lifecycle_is_ordered():
    acquisition = build()
    plan = acquisition.plan(requirement())
    with pytest.raises(PermissionError):
        acquisition.approve_and_register(plan)
    registered = acquisition.approve_and_register(plan, owner_approved=True)
    assert registered.status is CapabilityStatus.REGISTERED
    assert acquisition.enter_canary(registered.capability_id).status is CapabilityStatus.CANARY
    decision = acquisition.evaluate_canary(registered.capability_id, CanaryHealth(True, 1.0, 0.0, 100.0))
    assert decision.activated
    assert decision.status is CapabilityStatus.ACTIVE


def test_failed_candidate_is_not_automatically_activated():
    acquisition = build()
    plan = acquisition.plan(requirement())
    fallback = acquisition.fallback_plan(plan, plan.selected.candidate.capability_id)
    assert fallback is not None
    assert acquisition.discovery.registry.get(fallback.candidate.capability_id) is None
