import pytest

from devintel.runtime.app import DORMAMMURuntime
from devintel.executive import EvidenceRequirementError, Objective
from devintel.modules.research import Claim
from devintel.modules.research.synthesis import VerifiedClaim
from devintel.modules.research.verification import VerificationResult


def verified(subject, predicate, object_value, confidence, url):
    return VerifiedClaim(
        Claim(subject, predicate, object_value, confidence=confidence, evidence_urls=(url,)),
        VerificationResult(True, confidence, evidence_urls=(url,)),
    )


def test_runtime_exposes_evidence_backed_executive_understanding():
    runtime = DORMAMMURuntime()
    try:
        synthesis = runtime.synthesize_knowledge(
            "topic", [verified("A", "supports", "B", 0.9, "https://example.com/source")]
        )
        result = runtime.evidence_backed_understanding(
            Objective("act on findings", "meet the objective", "scope-1"), synthesis
        )
        assert result.understanding.success_criteria == ("A supports B",)
        assert result.provenance == ("https://example.com/source",)
    finally:
        runtime.close()


def test_runtime_evidence_path_fails_closed_without_eligible_evidence():
    runtime = DORMAMMURuntime()
    try:
        synthesis = runtime.synthesize_knowledge("topic", [])
        with pytest.raises(EvidenceRequirementError):
            runtime.evidence_backed_understanding(
                Objective("act on findings", "meet the objective", "scope-1"), synthesis
            )
    finally:
        runtime.close()
