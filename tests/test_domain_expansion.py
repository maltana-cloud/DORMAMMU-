from devintel.modules.research.domain_expansion import DomainEvidence, DomainExpander, DomainProposal
from devintel.modules.research.domain_registry import DomainRegistry


def proposal(*, verified=True, confidence=0.9, risks=(), required=("research",)):
    return DomainProposal(
        name="climate resilience",
        purpose="research adaptation opportunities",
        boundaries=("evidence analysis only",),
        evidence=(DomainEvidence("https://example.org/source", "supports domain relevance", confidence, verified),),
        risks=tuple(risks),
        required_capabilities=tuple(required),
    )


def test_verified_low_risk_proposal_is_eligible():
    item = proposal()
    assessment = DomainExpander().assess(item, ["research"])
    assert assessment.eligible is True
    assert DomainExpander.admission_allowed(assessment) is True


def test_unverified_proposal_is_rejected():
    assessment = DomainExpander().assess(proposal(verified=False), ["research"])
    assert assessment.eligible is False
    assert "no verified evidence" in assessment.reasons


def test_missing_capability_is_rejected():
    assessment = DomainExpander().assess(proposal(), [])
    assert assessment.eligible is False
    assert "required capabilities are not fully available" in assessment.reasons


def test_high_risk_proposal_is_rejected():
    assessment = DomainExpander().assess(proposal(risks=("r1", "r2", "r3")), ["research"])
    assert assessment.eligible is False
    assert "declared risk exceeds threshold" in assessment.reasons


def test_registry_requires_matching_eligible_assessment():
    item = proposal()
    assessment = DomainExpander().assess(item, ["research"])
    registry = DomainRegistry()
    record = registry.register(item, assessment)
    assert record.version == 1
    assert registry.get(item.proposal_id) == record


def test_registry_rejects_ineligible_proposals():
    item = proposal(verified=False)
    assessment = DomainExpander().assess(item, ["research"])
    registry = DomainRegistry()
    try:
        registry.register(item, assessment)
    except ValueError as exc:
        assert "not eligible" in str(exc)
    else:
        raise AssertionError("ineligible domain was registered")
