from devintel.intelligence.domain import DomainIntelligenceEngine
from devintel.modules.research.knowledge import Claim
from devintel.modules.research.synthesis import KnowledgeSynthesisEngine, VerifiedClaim
from devintel.modules.research.verification import VerificationResult


def verified(subject, predicate, object_value, confidence=0.9):
    claim = Claim(subject, predicate, object_value, confidence, ("https://example.com/evidence",))
    verification = VerificationResult(True, confidence, ("verified evidence",), ("https://example.com/evidence",))
    return VerifiedClaim(claim, verification)


def test_builds_bounded_domain_profile_from_synthesis():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "developer tooling",
        [
            verified("Developers", "need", "faster feedback", 0.9),
            verified("Teams", "use", "automated testing", 0.8),
        ],
    )
    result = DomainIntelligenceEngine().build("developer tooling", synthesis)
    assert result.domain == "developer tooling"
    assert len(result.signals) == 2
    assert result.signals[0].confidence == 0.9
    assert result.entities == ("Developers", "Teams")
    assert result.topics == ("automated testing", "faster feedback")
    assert result.uncertainty.startswith("bounded:")
    assert result.signals[0].evidence_urls == ("https://example.com/evidence",)


def test_rejects_unverified_raw_claims_and_non_synthesis_input():
    raw = Claim("Users", "need", "automation", 0.9, ("https://example.com/evidence",))
    try:
        DomainIntelligenceEngine().build("automation", raw)
        assert False
    except TypeError:
        pass


def test_contradictions_remain_uncertain():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "market",
        [
            verified("Users", "need", "automation", 0.9),
            verified("Users", "need", "manual workflows", 0.9),
        ],
    )
    result = DomainIntelligenceEngine().build("market", synthesis)
    assert result.uncertainty.startswith("high:")
    assert all(signal.uncertain for signal in result.signals)
    assert all(signal.confidence <= 0.49 for signal in result.signals)


def test_bounds_and_deterministically_orders_signals():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "tools",
        [
            verified("Zed", "uses", "B", 0.7),
            verified("Ada", "uses", "C", 0.9),
            verified("Ada", "needs", "A", 0.9),
        ],
    )
    result = DomainIntelligenceEngine(max_signals=2).build("tools", synthesis, limit=2)
    assert len(result.signals) == 2
    assert [(x.subject, x.predicate, x.object) for x in result.signals] == [
        ("Ada", "needs", "A"),
        ("Ada", "uses", "C"),
    ]


def test_validates_domain_and_limit():
    engine = DomainIntelligenceEngine(max_signals=2)
    synthesis = KnowledgeSynthesisEngine().synthesize("tools", [verified("Users", "need", "automation")])
    try:
        engine.build("", synthesis)
        assert False
    except ValueError:
        pass
    try:
        engine.build("tools", synthesis, limit=3)
        assert False
    except ValueError:
        pass
