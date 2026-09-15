from devintel.autonomy.evolution import EvolutionEngine, EvolutionEvaluation, EvolutionPolicy, ImprovementCandidate
from devintel.autonomy.learning import LearningProposal


def proposal(scope="x", subject="agent"):
    return LearningProposal(scope, ("c1", "c2", "c3"), "increase bounded routing preference", 0.2, 0.9, True, subject)


def test_candidates_require_verified_learning_volume():
    engine = EvolutionEngine()
    candidates = engine.candidates_from([proposal()])
    assert len(candidates) == 1
    assert candidates[0].target == "routing"


def test_evaluation_and_promotion_require_measured_gain():
    engine = EvolutionEngine(EvolutionPolicy(min_gain=0.1, min_confidence=0.8))
    candidate = engine.candidates_from([proposal()])[0]
    evaluation = engine.evaluate(candidate, lambda c: EvolutionEvaluation(c.candidate_id, True, 0.5, 0.7, 0.9, 3))
    promotion = engine.promote(candidate, evaluation)
    assert promotion.version == 1
    assert engine.active_version("x") == 1


def test_unsafe_or_weak_candidate_cannot_promote():
    engine = EvolutionEngine()
    candidate = engine.candidates_from([proposal()])[0]
    evaluation = EvolutionEvaluation(candidate.candidate_id, False, 0.5, 0.7, 0.9, 3, "safety regression")
    try:
        engine.promote(candidate, evaluation)
    except ValueError as exc:
        assert "promotion gates" in str(exc)
    else:
        raise AssertionError("unsafe evolution was promoted")


def test_stale_candidate_cannot_overwrite_newer_version():
    engine = EvolutionEngine()
    candidate = engine.candidates_from([proposal()])[0]
    evaluation = EvolutionEvaluation(candidate.candidate_id, True, 0.5, 0.7, 0.9, 3)
    engine.promote(candidate, evaluation)
    try:
        engine.promote(candidate, evaluation)
    except ValueError as exc:
        assert "stale" in str(exc)
    else:
        raise AssertionError("stale candidate was promoted")


def test_evolution_cannot_target_authority_or_security():
    for target in ("authority", "security", "secrets", "credentials", "owner_control", "recovery", "code"):
        try:
            ImprovementCandidate("id", "scope", target, "change", ("c1",), 0.1, 0.9)
        except ValueError as exc:
            assert "cannot target" in str(exc)
        else:
            raise AssertionError(f"forbidden target accepted: {target}")


def test_rollback_can_return_to_previous_version_only():
    engine = EvolutionEngine()
    candidate = engine.candidates_from([proposal()])[0]
    evaluation = EvolutionEvaluation(candidate.candidate_id, True, 0.5, 0.7, 0.9, 3)
    engine.promote(candidate, evaluation)
    assert engine.rollback("x", 0) == 0
    assert engine.active_version("x") == 0
