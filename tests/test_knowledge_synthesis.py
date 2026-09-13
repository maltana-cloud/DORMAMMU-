import pytest

from devintel.modules.research import Claim
from devintel.modules.research.synthesis import KnowledgeSynthesisEngine, VerifiedClaim
from devintel.modules.research.verification import VerificationResult


def verified(subject, predicate, object_value, confidence, url):
    claim = Claim(subject, predicate, object_value, confidence=confidence, evidence_urls=(url,))
    verification = VerificationResult(True, confidence, evidence_urls=(url,))
    return VerifiedClaim(claim, verification)


def test_synthesis_preserves_provenance_and_exposes_requirements():
    result = KnowledgeSynthesisEngine().synthesize(
        "test", [verified("A", "supports", "B", 0.9, "https://example.com/source")]
    )
    assert result.contradictions == ()
    assert result.provenance == ("https://example.com/source",)
    assert result.executive_requirements() == ("A supports B",)
    assert result.signals[0].confidence == 0.9


def test_contradictory_verified_claims_are_explicit_and_uncertain():
    result = KnowledgeSynthesisEngine().synthesize("test", [
        verified("A", "supports", "B", 0.9, "https://example.com/a"),
        verified("A", "supports", "C", 0.9, "https://example.com/c"),
    ])
    assert len(result.contradictions) == 1
    assert all(signal.uncertain for signal in result.signals)
    assert all(signal.confidence < 0.5 for signal in result.signals)
    assert result.executive_requirements() == ()
    assert "contradictory" in result.uncertainty


def test_unverified_claim_cannot_enter_verified_claim_contract():
    claim = Claim("A", "supports", "B", confidence=1.0, evidence_urls=("https://example.com/source",))
    verification = VerificationResult(False, 0.1, reasons=("not verified",))
    with pytest.raises(ValueError):
        VerifiedClaim(claim, verification)


def test_non_verified_input_is_excluded_instead_of_becoming_truth():
    valid = verified("A", "supports", "B", 0.9, "https://example.com/source")
    result = KnowledgeSynthesisEngine().synthesize("test", [valid, object()], excluded_claims=2)
    assert result.excluded_claims == 3
    assert result.executive_requirements() == ("A supports B",)


def test_normalized_equivalent_objects_are_not_false_contradictions():
    result = KnowledgeSynthesisEngine().synthesize("test", [
        verified(" A ", " supports ", " B ", 0.8, "https://example.com/a"),
        verified("A", "supports", "B", 0.9, "https://example.com/b"),
    ])
    assert result.contradictions == ()
    assert result.signals[0].statement == "A supports B"
    assert result.signals[0].confidence == 0.9


def test_evidence_urls_are_canonicalized_and_invalid_urls_do_not_become_provenance():
    result = KnowledgeSynthesisEngine().synthesize(
        "test", [verified("A", "supports", "B", 0.9, "HTTPS://Example.com/source/#fragment")]
    )
    assert result.provenance == ("https://example.com/source",)


def test_empty_verified_evidence_is_explicitly_uncertain():
    result = KnowledgeSynthesisEngine().synthesize("empty", [])
    assert result.signals == ()
    assert result.provenance == ()
    assert result.executive_requirements() == ()
    assert "no verified claims" in result.uncertainty


def test_negative_exclusion_count_is_rejected():
    with pytest.raises(ValueError):
        KnowledgeSynthesisEngine().synthesize("test", [], excluded_claims=-1)
