from devintel.autonomy import EvolutionEvaluation, LearningProposal
from devintel.ecosystem import EcosystemEvolutionEngine, EvolutionCyclePolicy


def proposal(scope="research"):
    return LearningProposal(scope, ("c1", "c2", "c3"), "increase bounded strategy weight", 0.2, 0.9)


def evaluation(candidate, *, safe=True, delta=0.2, confidence=0.9, evidence=3):
    return EvolutionEvaluation(candidate.candidate_id, safe, 0.1, 0.1 + delta, confidence, evidence)


def test_cycle_promotes_safe_measurable_change():
    engine = EcosystemEvolutionEngine()
    result = engine.run([proposal()], lambda c: evaluation(c))
    assert len(result.promotions) == 1
    assert engine.evolution.active_version("research") == 1


def test_cycle_bounds_proposals_and_blocks_unhealthy_scope():
    engine = EcosystemEvolutionEngine(policy=EvolutionCyclePolicy(max_proposals=1, max_candidates=1))
    result = engine.run([proposal(), proposal("other")], lambda c: evaluation(c), capability_health={"research": False})
    assert result.proposals_seen == 1
    assert result.promotions == ()
    assert result.blocked == 1


def test_unsafe_evaluation_is_not_promoted():
    engine = EcosystemEvolutionEngine()
    result = engine.run([proposal()], lambda c: evaluation(c, safe=False))
    assert result.promotions == ()
    assert result.rejected == 1


def test_rollback_never_moves_forward():
    engine = EcosystemEvolutionEngine()
    result = engine.run([proposal()], lambda c: evaluation(c))
    assert result.promotions
    assert engine.rollback("research", 0) == 0
    assert engine.evolution.active_version("research") == 0


def test_protected_targets_are_rejected_by_underlying_evolution_contract():
    from devintel.autonomy.evolution import ImprovementCandidate
    from datetime import datetime, timezone
    try:
        ImprovementCandidate("x", "scope", "security", "change", ("c1", "c2", "c3"), 0.2, 0.9, created_at=datetime.now(timezone.utc))
    except ValueError:
        pass
    else:
        raise AssertionError("protected evolution target was accepted")
