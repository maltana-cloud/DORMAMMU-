from devintel.intelligence.problem_opportunity import ProblemOpportunityEngine
from devintel.modules.research.knowledge import Claim
from devintel.modules.research.synthesis import KnowledgeSynthesisEngine, VerifiedClaim
from devintel.modules.research.verification import VerificationResult


def verified(statement_subject, predicate, object_value, confidence=0.9):
    claim = Claim(statement_subject, predicate, object_value, confidence, ("https://example.com/evidence",))
    verification = VerificationResult(True, confidence, ("https://example.com/evidence",), "verified evidence")
    return VerifiedClaim(claim, verification)


def test_identifies_and_ranks_evidence_backed_problem():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "developer workflows",
        [verified("Developers", "need", "faster build feedback")],
    )
    result = ProblemOpportunityEngine().identify(synthesis)
    assert len(result.candidates) == 1
    assert result.candidates[0].kind == "problem"
    assert result.candidates[0].confidence == 0.9
    assert result.candidates[0].evidence_urls == ("https://example.com/evidence",)


def test_identifies_opportunity_without_treating_money_as_value():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "market",
        [verified("Teams", "see", "unmet demand", 0.8)],
    )
    result = ProblemOpportunityEngine().identify(synthesis)
    assert result.candidates[0].kind == "opportunity"
    assert result.candidates[0].score <= 1.0


def test_contradictions_remain_uncertain():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "market",
        [
            verified("Users", "need", "automation", 0.9),
            verified("Users", "need", "manual workflows", 0.9),
        ],
    )
    result = ProblemOpportunityEngine().identify(synthesis)
    assert result.uncertainty.startswith("high:")
    assert all(candidate.uncertain for candidate in result.candidates)
    assert all(candidate.confidence <= 0.49 for candidate in result.candidates)


def test_ignores_unrelated_verified_statements():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "topic",
        [verified("System", "uses", "Python", 0.95)],
    )
    result = ProblemOpportunityEngine().identify(synthesis)
    assert result.candidates == ()
    assert result.uncertainty.startswith("high:")


def test_bounds_results_and_validates_inputs():
    synthesis = KnowledgeSynthesisEngine().synthesize(
        "topic",
        [verified(f"Users {i}", "need", "better tooling", 0.7) for i in range(5)],
    )
    engine = ProblemOpportunityEngine(max_candidates=2)
    result = engine.identify(synthesis, limit=2)
    assert len(result.candidates) == 2
    assert result.excluded >= 3
    try:
        engine.identify(synthesis, limit=3)
        assert False
    except ValueError:
        pass
    try:
        engine.identify(object())
        assert False
    except TypeError:
        pass
