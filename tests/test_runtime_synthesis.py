from devintel.modules.research import Claim, VerifiedClaim
from devintel.modules.research.verification import VerificationResult
from devintel.runtime import DORMAMMURuntime


def verified(subject, predicate, object_value, confidence, url):
    claim = Claim(subject, predicate, object_value, confidence=confidence, evidence_urls=(url,))
    return VerifiedClaim(claim, VerificationResult(True, confidence, evidence_urls=(url,)))


def test_runtime_exposes_evidence_synthesis_without_granting_authority():
    runtime = DORMAMMURuntime()
    try:
        result = runtime.synthesize_knowledge(
            "test", [verified("system", "needs", "evidence", 0.9, "https://example.com/source")]
        )
        assert result.executive_requirements() == ("system needs evidence",)
        assert result.provenance == ("https://example.com/source",)
    finally:
        runtime.close()


def test_runtime_synthesis_blocks_contradictory_requirements():
    runtime = DORMAMMURuntime()
    try:
        result = runtime.synthesize_knowledge("test", [
            verified("system", "needs", "A", 0.9, "https://example.com/a"),
            verified("system", "needs", "B", 0.9, "https://example.com/b"),
        ])
        assert len(result.contradictions) == 1
        assert result.executive_requirements() == ()
    finally:
        runtime.close()
