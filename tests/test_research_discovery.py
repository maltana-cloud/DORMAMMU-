from devintel.modules.research.contracts import ResearchCandidate
from devintel.modules.research.discovery import ResearchDiscoveryEngine


class Provider:
    def __init__(self, items):
        self.items = items

    def discover(self, query, *, limit):
        return self.items[:limit]


def test_discovery_deduplicates_canonical_urls_and_bounds_results():
    providers = [
        Provider([ResearchCandidate("https://example.com/a#fragment", "A")]),
        Provider([ResearchCandidate("https://EXAMPLE.com/a", "Duplicate"), ResearchCandidate("https://example.com/b", "B")]),
    ]
    result = ResearchDiscoveryEngine(providers).discover("test", limit=2)
    assert [item.url for item in result.candidates] == ["https://example.com/a", "https://example.com/b"]


def test_discovery_rejects_bad_provider_output_without_crossing_trust_boundary():
    class BadProvider:
        def discover(self, query, *, limit):
            return ["not a candidate"]

    result = ResearchDiscoveryEngine([BadProvider()]).discover("test")
    assert result.candidates == ()
    assert result.rejected == 1


def test_discovery_provider_failure_is_isolated():
    class Failing:
        def discover(self, query, *, limit):
            raise RuntimeError("provider unavailable")

    result = ResearchDiscoveryEngine([Failing(), Provider([ResearchCandidate("https://example.com/x")])]).discover("test")
    assert len(result.candidates) == 1
    assert result.rejected == 1
