from datetime import datetime, timezone
import pytest
from devintel.autonomy.learning import OutcomeEvidence, OutcomeLearner

def ev(scope, cycle, metric, verified=True):
    return OutcomeEvidence(scope, cycle, True, verified, metric, recorded_at=datetime.now(timezone.utc))

def test_learning_requires_verified_same_scope_and_enough_samples():
    learner = OutcomeLearner(min_samples=3)
    assert learner.reflect([ev("s", "1", .5), ev("s", "2", .4)]) == ()
    proposal = learner.reflect([ev("s", "1", .5), ev("s", "2", .4), ev("s", "3", .6)])
    assert proposal[0].scope_id == "s"
    assert proposal[0].reversible is True
    with pytest.raises(ValueError):
        learner.reflect([ev("s", "1", .5), ev("other", "2", .5), ev("s", "3", .5)])

def test_unverified_outcome_cannot_enter_learning():
    with pytest.raises(ValueError): ev("s", "1", .5, verified=False)

def test_learning_never_emits_authority_or_code_mutation():
    proposal = OutcomeLearner(min_samples=2, min_confidence=.5).reflect([ev("s", "1", .2), ev("s", "2", .4)])
    assert "permission" not in proposal[0].adjustment
    assert "authority" not in proposal[0].adjustment
    assert proposal[0].reversible
