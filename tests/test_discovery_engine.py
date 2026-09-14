from devintel.capabilities import (
    CapabilityResourceDiscoveryEngine,
    CapabilitySourceConfig,
    DiscoveryPolicy,
    ResourceKind,
)


def test_refresh_local_inventory_is_read_only_and_bounded():
    engine = CapabilityResourceDiscoveryEngine()
    snapshot = engine.refresh_local_inventory()
    assert "runtime.local" in snapshot.capabilities
    assert "host:cpu" in snapshot.resources
    assert "host:storage" in snapshot.resources
    engine.close()


def test_source_requires_active_trust_policy():
    engine = CapabilityResourceDiscoveryEngine(discovery_policy=DiscoveryPolicy(trusted_evidence_sources=("trusted",)))
    config = CapabilitySourceConfig("catalog", "https://catalog.example/capabilities", "publisher", "other")
    try:
        engine.add_source(config)
        assert False, "untrusted source must not be connected"
    except PermissionError:
        pass
    finally:
        engine.close()


def test_cpu_resource_can_be_selected_after_inventory():
    engine = CapabilityResourceDiscoveryEngine()
    engine.refresh_local_inventory()
    decision = engine.decide_resource(ResourceKind.CPU, 1)
    assert decision.granted
    assert decision.resource_id == "host:cpu"
    engine.close()
