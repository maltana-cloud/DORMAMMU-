from devintel.capabilities.discovery import DiscoveryPolicy
from devintel.capabilities.sources import CapabilitySourceConfig, CapabilitySourceStore, ConfiguredCapabilitySource


def test_source_config_requires_https_and_is_disabled_by_default():
    try:
        CapabilitySourceConfig("x", "http://example.com/catalog", "Example", "example")
    except ValueError:
        pass
    else:
        raise AssertionError("HTTP source must be rejected")
    cfg = CapabilitySourceConfig("x", "https://example.com/catalog", "Example", "example")
    assert not cfg.enabled


def test_source_store_round_trip_and_enabled_order():
    store = CapabilitySourceStore()
    store.upsert(CapabilitySourceConfig("b", "https://b.example/catalog", "B", "b", enabled=True))
    store.upsert(CapabilitySourceConfig("a", "https://a.example/catalog", "A", "a", enabled=True))
    assert tuple(x.source_id for x in store.enabled()) == ("a", "b")
    assert store.get("a").publisher == "A"
    store.close()


def test_disabled_or_untrusted_source_cannot_be_constructed():
    disabled = CapabilitySourceConfig("x", "https://example.com/catalog", "Example", "example")
    try:
        ConfiguredCapabilitySource(disabled, discovery_policy=DiscoveryPolicy(trusted_evidence_sources=("example",), require_provenance=True))
    except PermissionError:
        pass
    else:
        raise AssertionError("disabled source must fail closed")

    enabled = CapabilitySourceConfig("x", "https://example.com/catalog", "Example", "example", enabled=True)
    try:
        ConfiguredCapabilitySource(enabled, discovery_policy=DiscoveryPolicy(trusted_evidence_sources=("other",), require_provenance=True))
    except PermissionError:
        pass
    else:
        raise AssertionError("untrusted source must fail closed")
