from devintel.runtime import DORMAMMURuntime
from devintel.capabilities import ResourceKind, ResourceRequest


def test_runtime_registers_local_inventory_and_exposes_observations():
    runtime = DORMAMMURuntime()
    try:
        resources = runtime.refresh_local_inventory()
        kinds = {item.kind for item in resources}
        assert ResourceKind.CPU in kinds
        assert ResourceKind.RAM in kinds
        assert ResourceKind.STORAGE in kinds
        observations = runtime.capability_observations("test-scope")
        assert {item.kind for item in observations} == {"capability_inventory", "resource_inventory", "capability_gaps", "resource_reservations"}
        assert all(item.scope_id == "test-scope" for item in observations)
    finally:
        runtime.close()


def test_runtime_can_reserve_and_release_local_cpu():
    runtime = DORMAMMURuntime()
    try:
        result = runtime.reserve_resource(ResourceRequest(ResourceKind.CPU, quantity=1))
        assert result.granted
        assert result.reservation_id
        assert len(runtime.resource_reservations()) == 1
        runtime.release_resource(result.reservation_id)
        assert runtime.resource_reservations() == ()
    finally:
        runtime.close()


def test_runtime_discovery_records_a_gap():
    runtime = DORMAMMURuntime()
    try:
        from devintel.capabilities import CapabilityRequirement
        result = runtime.discover_capabilities(CapabilityRequirement("missing", "need missing capability"))
        assert result.gap.gap_id == "gap:missing"
        assert result.candidates == ()
        assert runtime.capability_observations("scope")[2].data[0] == result.gap
    finally:
        runtime.close()
