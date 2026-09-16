from devintel.intelligence.autonomous_frontier import IntelligenceFrontier
from devintel.modules.research.knowledge import Claim
from devintel.modules.research.synthesis import KnowledgeSynthesisEngine, VerifiedClaim
from devintel.modules.research.verification import VerificationResult


def verified(subject, predicate, object_value, confidence=0.9):
    claim = Claim(subject, predicate, object_value, confidence, ("https://example.com/evidence",))
    verification = VerificationResult(True, confidence, (), ("https://example.com/evidence",))
    return VerifiedClaim(claim, verification)


def test_verified_synthesis_derives_bounded_objectives_and_mission_proposals():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "developer workflows",
        [verified("Developers", "need", "faster build feedback")],
    )
    result = IntelligenceFrontier().derive(synthesis, scope_id="engineering")

    assert result.topic == "developer workflows"
    assert len(result.objective_candidates) == 1
    assert result.objective_candidates[0].scope_id == "engineering"
    assert result.objective_candidates[0].source == "synthesis:problem"
    assert len(result.mission_proposals) == 1
    assert result.mission_proposals[0].scope_id == "engineering"
    assert result.mission_proposals[0].evidence_urls == ("https://example.com/evidence",)


def test_uncertain_contradictions_do_not_become_mission_proposals():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "market",
        [
            verified("Users", "need", "automation"),
            verified("Users", "need", "manual workflows"),
        ],
    )
    result = IntelligenceFrontier().derive(synthesis, scope_id="market")

    assert all(candidate.confidence <= 0.49 for candidate in result.objective_candidates)
    assert result.mission_proposals == ()


def test_objective_ids_are_deterministic_and_scope_bound():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "topic",
        [verified("Teams", "need", "better tooling")],
    )
    frontier = IntelligenceFrontier()
    first = frontier.derive(synthesis, scope_id="scope-a")
    second = frontier.derive(synthesis, scope_id="scope-a")
    other = frontier.derive(synthesis, scope_id="scope-b")

    assert first.objective_candidates == second.objective_candidates
    assert first.objective_candidates[0].objective_id != other.objective_candidates[0].objective_id
