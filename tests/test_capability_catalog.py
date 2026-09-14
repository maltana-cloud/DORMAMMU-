import json

from devintel.capabilities import CatalogPolicy, CapabilityDiscovery, CapabilityRequirement, DefaultEvaluator, DiscoveryPolicy, JsonCatalogScout


def test_json_catalog_scout_emits_provenanced_candidates():
    payload = json.dumps({"capabilities": [{
        "capability_id": "search-v1", "name": "Search", "version": "1.0", "interfaces": ["research"],
        "provider": "catalog-provider", "license": "MIT", "cost": 0,
        "permissions": ["approved"], "metadata": {"security_status": "verified", "performance": "verified"},
    }]})
    scout = JsonCatalogScout(payload, source="trusted-catalog", publisher="catalog", reference="https://catalog.example/search-v1")
    engine = CapabilityDiscovery(evaluator=DefaultEvaluator(DiscoveryPolicy(trusted_evidence_sources=("trusted-catalog",), require_provenance=True)))
    engine.add_scout(scout)
    result = engine.discover(CapabilityRequirement("research.search", "find sources", ("research",)))
    assert result.evaluations[0].eligible
    assert result.candidates[0].evidence[0].reference.endswith("search-v1")


def test_catalog_policy_is_bounded():
    policy = CatalogPolicy(timeout_seconds=5, max_bytes=1000, allowed_hosts=("catalog.example",))
    assert policy.max_bytes == 1000
