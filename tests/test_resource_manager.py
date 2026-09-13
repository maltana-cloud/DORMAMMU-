import pytest

from devintel.capabilities import ResourceDescriptor, ResourceKind, ResourceManager, ResourceRegistry, ResourceRequest


def manager():
    registry = ResourceRegistry()
    registry.register(ResourceDescriptor(
        "test:cpu", ResourceKind.CPU, "test cpu", capacity="4", availability="ready",
        permissions=("approved",), metadata={"allocatable": "4"},
    ))
    registry.register(ResourceDescriptor(
        "test:ram", ResourceKind.RAM, "test ram", capacity="100", availability="ready",
        permissions=("approved",), metadata={"allocatable": "100"},
    ))
    return ResourceManager(registry)


def test_reserve_and_release_cpu_capacity():
    resources = manager()
    first = resources.reserve(ResourceRequest(ResourceKind.CPU, quantity=3))
    assert first.granted and first.resource_id == "test:cpu" and first.reservation_id
    blocked = resources.reserve(ResourceRequest(ResourceKind.CPU, quantity=2))
    assert not blocked.granted
    resources.release(first.reservation_id)
    available = resources.reserve(ResourceRequest(ResourceKind.CPU, quantity=2))
    assert available.granted


def test_cost_limit_and_permission_are_enforced():
    resources = manager()
    assert resources.decide(ResourceRequest(ResourceKind.CPU, quantity=1, max_cost=0)).granted
    resources.registry.register(ResourceDescriptor(
        "test:paid", ResourceKind.GPU, "paid gpu", capacity="1", availability="ready",
        cost=1.0, permissions=(), metadata={"allocatable": "1"},
    ))
    assert not resources.decide(ResourceRequest(ResourceKind.GPU, max_cost=1.0)).granted


def test_unknown_capacity_fails_closed():
    registry = ResourceRegistry()
    registry.register(ResourceDescriptor("test:unknown", ResourceKind.GPU, "unknown gpu", availability="declared", permissions=("approved",)))
    resources = ResourceManager(registry)
    decision = resources.decide(ResourceRequest(ResourceKind.GPU, quantity=1))
    assert not decision.granted
    reservation = resources.reserve(ResourceRequest(ResourceKind.GPU, quantity=1))
    assert not reservation.granted


def test_invalid_request_is_rejected():
    with pytest.raises(ValueError):
        ResourceRequest(ResourceKind.CPU, quantity=0)
