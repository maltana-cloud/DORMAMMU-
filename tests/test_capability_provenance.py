from devintel.capabilities import CapabilityDescriptor, CapabilityEvidence, CapabilityRegistry, CapabilityRegistryStore, CapabilityStatus


def candidate():
    evidence = (CapabilityEvidence("catalog", "2026-09-14T00:00:00+00:00", "trusted-catalog", "https://catalog.example/capabilities/x", "0123456789abcdef"),)
    return CapabilityDescriptor("search", "Search", "1.0", ("research",), "trusted", "MIT", evidence=evidence)


def test_evidence_requires_valid_timestamp_and_http_references():
    CapabilityEvidence("catalog", "2026-09-14T00:00:00+00:00", "publisher", "https://example.com/item", "0123456789abcdef")
    assert CapabilityEvidence("catalog", "2026-09-14T00:00:00+00:00", "publisher", signature_verified=True).trustworthy


def test_registry_store_survives_reopen(tmp_path):
    path = tmp_path / "capabilities.sqlite"
    store = CapabilityRegistryStore(path)
    registry = CapabilityRegistry(store=store)
    registry.register(candidate())
    store.close()

    reopened_store = CapabilityRegistryStore(path)
    reopened = CapabilityRegistry(store=reopened_store)
    restored = reopened.get("search")
    assert restored is not None
    assert restored.status is CapabilityStatus.DISCOVERED
    assert restored.evidence[0].publisher == "trusted-catalog"
    reopened_store.close()
