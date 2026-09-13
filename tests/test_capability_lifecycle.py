import pytest
from dataclasses import replace
from devintel.capabilities import (
    CapabilityDescriptor, CapabilityLifecycle, CapabilityRegistry, CapabilityStatus,
    DefaultEvaluator, DiscoveryPolicy, CapabilityRequirement,
)


def descriptor(status=CapabilityStatus.DISCOVERED):
    return CapabilityDescriptor("research", "Research", "1.0", ("research",), "trusted", "MIT", status=status, permissions=("approved",))


def test_lifecycle_requires_valid_order_and_reason():
    registry = CapabilityRegistry()
    registry.register(descriptor())
    lifecycle = CapabilityLifecycle(registry)
    with pytest.raises(ValueError):
        lifecycle.transition("research", CapabilityStatus.ACTIVE, "skip")
    with pytest.raises(ValueError):
        lifecycle.transition("research", CapabilityStatus.EVALUATED, "")


def test_lifecycle_approval_requires_explicit_permission():
    registry = CapabilityRegistry()
    candidate = descriptor()
    req = CapabilityRequirement("research", "research", ("research",))
    evaluation = DefaultEvaluator(DiscoveryPolicy()).evaluate(req, candidate)
    lifecycle = CapabilityLifecycle(registry)
    with pytest.raises(PermissionError):
        lifecycle.approve(evaluation)
    approved = lifecycle.approve(evaluation, permission_granted=True)
    assert approved.status is CapabilityStatus.APPROVED


def test_lifecycle_canary_activate_and_rollback():
    registry = CapabilityRegistry()
    registry.register(descriptor(CapabilityStatus.REGISTERED))
    lifecycle = CapabilityLifecycle(registry)
    assert lifecycle.canary("research").status is CapabilityStatus.CANARY
    assert lifecycle.activate("research").status is CapabilityStatus.ACTIVE
    assert lifecycle.degrade("research", "health check failed").status is CapabilityStatus.DEGRADED
    assert lifecycle.rollback("research", "canary failure").status is CapabilityStatus.ROLLED_BACK


def test_rollback_can_return_to_canary_only_explicitly():
    registry = CapabilityRegistry()
    registry.register(descriptor(CapabilityStatus.ROLLED_BACK))
    lifecycle = CapabilityLifecycle(registry)
    assert lifecycle.canary("research").status is CapabilityStatus.CANARY
