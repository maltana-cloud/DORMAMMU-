from datetime import datetime, timezone
import pytest
from devintel.autonomy.learning import OutcomeEvidence, OutcomeLearner
from devintel.autonomy.learning_store import LearningStore
from devintel.autonomy.mission_learning import MissionLearningBridge
from devintel.autonomy.next_objective import NextObjectiveSelector, ObjectiveCandidate


def evidence(scope: str, cycle: str, metric: float, subject: str = "") -> OutcomeEvidence:
    return OutcomeEvidence(scope, cycle, metric >= 0, True, metric, recorded_at=datetime.fromtimestamp(int(cycle), timezone.utc), subject_id=subject)


def candidates():
    return (
        ObjectiveCandidate("a", "objective A", "s", "gap", .2),
        ObjectiveCandidate("b", "objective B", "s", "gap", .1),
    )


def test_verified_outcome_persists_and_drives_bounded_learning():
    store = LearningStore()
    bridge = MissionLearningBridge(store, learner=OutcomeLearner(min_samples=2, min_confidence=.5))
    bridge.transition(evidence("s", "1", .4))
    result = bridge.transition(evidence("s", "2", .6), candidates())
    assert len(store.outcomes("s")) == 2
    assert result.proposals
    assert result.next_objective is not None
    assert result.next_objective.candidate.objective_id == "a"


def test_duplicate_verified_outcome_and_learning_transition_are_idempotent():
    store = LearningStore()
    bridge = MissionLearningBridge(store, learner=OutcomeLearner(min_samples=2, min_confidence=.5))
    e1, e2 = evidence("s", "1", .5), evidence("s", "2", .5)
    bridge.transition(e1)
    bridge.transition(e2)
    bridge.transition(e2, candidates())
    assert len(store.outcomes("s")) == 2
    assert len(store.proposals("s")) == 1


def test_learning_rejects_mixed_scope_and_unverified_state():
    store = LearningStore()
    bridge = MissionLearningBridge(store)
    with pytest.raises(ValueError):
        bridge.transition(evidence("s", "1", .2), (ObjectiveCandidate("a", "A", "other", "gap"),))
    with pytest.raises(ValueError):
        NextObjectiveSelector().select(candidates(), verified_outcomes=(evidence("s", "1", .2),))


def test_selection_is_deterministic_for_same_state():
    selector = NextObjectiveSelector()
    first = selector.select(candidates())
    second = selector.select(tuple(reversed(candidates())))
    assert first == second


def test_selection_is_bounded_and_authority_free():
    selector = NextObjectiveSelector(max_candidates=1)
    selected = selector.select(candidates())
    assert selected is not None
    assert selected.candidate.objective_id == "a"
    assert "authority" not in selected.rationale
