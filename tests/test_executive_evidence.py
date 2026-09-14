import pytest

from devintel.executive import EvidenceBackedExecutiveAdapter, EvidenceRequirementError, Objective
from devintel.modules.research import Claim
from devintel.modules.research.synthesis import KnowledgeSynthesisEngine, VerifiedClaim
from devintel.modules.research.verification import VerificationResult


def verified(subject, predicate, object_value, confidence, url):
    claim = Claim(subject, predicate, object_value, confidence=confidence, evidence_urls=(url,))
    verification = VerificationResult(True, confidence, evidence_urls=(url,))
    return VerifiedClaim(claim, verification)


def objective():
    return Objective("act on verified findings", "complete the bounded objective", "scope-1")


def test_adapter_turns_eligible_synthesis_into_explicit_success_criteria():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "topic", [verified("A", "supports", "B", 0.9, "https://example.com/source")]
    )
    result = EvidenceBackedExecutiveAdapter().understand(objective(), synthesis)
    understanding = result.understanding
    assert understanding.success_criteria == ("A supports B",)
    assert understanding.evidence_urls == ("https://example.com/source",)
    assert understanding.evidence_topic == "topic"
    assert understanding.evidence_uncertainty == synthesis.uncertainty
    assert understanding.constraints["evidence_topic"] == "topic"


def test_adapter_rejects_contradictory_synthesis_with_no_eligible_requirements():
    synthesis = KnowledgeSynthesisEngine().synthesize("topic", [
        verified("A", "supports", "B", 0.9, "https://example.com/a"),
        verified("A", "supports", "C", 0.9, "https://example.com/c"),
    ])
    with pytest.raises(EvidenceRequirementError):
        EvidenceBackedExecutiveAdapter().understand(objective(), synthesis)


def test_adapter_rejects_low_confidence_synthesis():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "topic", [verified("A", "supports", "B", 0.49, "https://example.com/source")]
    )
    with pytest.raises(EvidenceRequirementError):
        EvidenceBackedExecutiveAdapter().understand(objective(), synthesis)
