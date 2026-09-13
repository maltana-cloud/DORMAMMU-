from devintel.capabilities import (
    CapabilityDescriptor,
    CapabilityLifecycle,
    CapabilityRegistry,
    CapabilityStatus,
    CanaryHealth,
    CanaryMonitor,
)


def make_registry(status=CapabilityStatus.REGISTERED):
    registry = CapabilityRegistry()
    registry.register(CapabilityDescriptor("cap", "Capability", "1.0", ("x",), "trusted", "MIT", status=status))
    return registry


def test_healthy_canary_activates():
    registry = make_registry()
    lifecycle = CapabilityLifecycle(registry)
    lifecycle.canary("cap")
    monitor = CanaryMonitor(lifecycle)
    decision = monitor.evaluate("cap", CanaryHealth(True, 0.999, 0.001, 100.0))
    assert decision.activated
    assert not decision.rolled_back
    assert registry.get("cap").status is CapabilityStatus.ACTIVE


def test_unhealthy_canary_rolls_back():
    registry = make_registry()
    lifecycle = CapabilityLifecycle(registry)
    lifecycle.canary("cap")
    monitor = CanaryMonitor(lifecycle)
    decision = monitor.evaluate("cap", CanaryHealth(True, 0.90, 0.10, 100.0, "provider unstable"))
    assert not decision.activated
    assert decision.rolled_back
    assert registry.get("cap").status is CapabilityStatus.ROLLED_BACK


def test_active_capability_degrades_then_rolls_back_on_bad_health():
    registry = make_registry()
    lifecycle = CapabilityLifecycle(registry)
    lifecycle.canary("cap")
    lifecycle.activate("cap")
    decision = CanaryMonitor(lifecycle).evaluate("cap", CanaryHealth(False, 0.5, 0.5, 9000.0))
    assert decision.rolled_back
    assert registry.get("cap").status is CapabilityStatus.ROLLED_BACK
