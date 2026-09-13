from devintel.runtime import DORMAMMURuntime
from devintel.capabilities import ResourceKind


def test_runtime_registers_local_inventory_and_exposes_observations():
    runtime = DORMAMMURuntime()
    resources = runtime.refresh_local_inventory()
    kinds = {item.kind for item in resources}
    assert ResourceKind.CPU in kinds
    assert ResourceKind.RAM in kinds
    assert ResourceKind.STORAGE in kinds
    observations = runtime.capability_observations("test-scope")
    assert {item.kind for item in observations} == {"capability_inventory", "resource_inventory", "capability_gaps"}
    assert all(item.scope_id == "test-scope" for item in observations)


def test_runtime_discovery_records_a_gap():
    runtime = DORMAMMURuntime()
    from devintel.capabilities import CapabilityRequirement
    result = runtime.discover_capabilities(CapabilityRequirement("missing", "need missing capability"))
    assert result.gap.gap_id == "gap:missing"
    assert result.candidates == ()
    assert runtime.capability_observations("scope")[-1].data[0] == result.gap
