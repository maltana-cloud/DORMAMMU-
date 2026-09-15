import pytest

from devintel.intelligence.collaboration import CollaborationStatus, HumanCollaborationEngine


def test_creates_deterministic_reviewable_request():
    engine = HumanCollaborationEngine()
    first = engine.create_request("research", "validate this hypothesis", context="Need human judgment.", evidence=("https://example.com/source",))
    second = engine.create_request("research", "validate this hypothesis", context="Need human judgment.", evidence=("https://example.com/source",))
    assert first == second
    assert first.status is CollaborationStatus.PENDING
    assert first.evidence == ("https://example.com/source",)


def test_request_identity_uses_normalized_bounded_content():
    engine = HumanCollaborationEngine()
    request = engine.create_request(
        " Research ",
        " validate this hypothesis ",
        context="  Need human judgment.  ",
        evidence=(" https://example.com/source ", ""),
    )
    equivalent = engine.create_request(
        "research",
        "validate this hypothesis",
        context="Need human judgment.",
        evidence=("https://example.com/source",),
    )
    assert request == equivalent


def test_invalid_evidence_is_rejected_before_identity_is_created():
    engine = HumanCollaborationEngine()
    with pytest.raises(TypeError):
        engine.create_request("scope", "objective", evidence=("valid", 123))
    with pytest.raises(TypeError):
        engine.create_request("scope", "objective", evidence="not-a-sequence")


def test_human_response_updates_only_pending_request_status():
    engine = HumanCollaborationEngine()
    request = engine.create_request("research", "review finding")
    response = engine.respond(request, "human-1", "Reviewed; proceed to analysis.", accepted=True)
    updated = engine.apply_response(request, response)
    assert updated.status is CollaborationStatus.ACCEPTED
    assert updated.request_id == request.request_id
    assert updated.objective == request.objective

    with pytest.raises(ValueError):
        engine.apply_response(updated, response)


def test_rejection_is_explicit_and_mismatched_response_fails():
    engine = HumanCollaborationEngine()
    request = engine.create_request("research", "review finding")
    response = engine.respond(request, "human-1", "Insufficient evidence.", accepted=False, reason="evidence gap")
    assert engine.apply_response(request, response).status is CollaborationStatus.REJECTED
    other = engine.create_request("other", "different task")
    with pytest.raises(ValueError):
        engine.apply_response(other, response)


def test_bounds_are_enforced():
    engine = HumanCollaborationEngine(max_context=5, max_evidence=1)
    with pytest.raises(ValueError):
        engine.create_request("scope", "objective", context="123456")
    with pytest.raises(ValueError):
        engine.create_request("scope", "objective", evidence=("a", "b"))
