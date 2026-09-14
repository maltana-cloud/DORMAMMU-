from datetime import datetime, timezone

import pytest

from devintel.executive.cognition import CognitiveFact, CognitiveHypothesis, CognitiveSelfModel, CognitiveState


def test_cognitive_fact_and_hypothesis_are_bounded_and_typed():
    fact = CognitiveFact("verified fact", 0.9, ("https://example.com",), "scope")
    hypothesis = CognitiveHypothesis("uncertain possibility", 0.4, ("https://example.com",))
    state = CognitiveState("scope", (fact,), (hypothesis,), (), CognitiveSelfModel(("cap",), ("cpu",), ("no external authority",), datetime.now(timezone.utc)))
    assert state.state_id
    assert state.self_model.capability_ids == ("cap",)


def test_cognitive_state_diff_is_deterministic():
    base = CognitiveState("scope", (CognitiveFact("a", 1.0),))
    newer = CognitiveState("scope", (CognitiveFact("a", 1.0), CognitiveFact("b", 0.8)))
    from devintel.executive.cognition import CoreCognition
    assert CoreCognition().compare(base, newer) == ("b",)


def test_cognitive_state_diff_rejects_cross_scope():
    from devintel.executive.cognition import CoreCognition
    with pytest.raises(ValueError):
        CoreCognition().compare(CognitiveState("a"), CognitiveState("b"))


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError):
        CognitiveFact("fact", 1.1)
