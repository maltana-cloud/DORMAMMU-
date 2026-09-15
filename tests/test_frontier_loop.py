from datetime import datetime, timezone
from devintel.autonomy.learning_store import LearningStore
from devintel.autonomy.mission_learning import MissionLearningBridge
from devintel.autonomy.learning import OutcomeLearner
from devintel.autonomy.next_objective import ObjectiveCandidate
from devintel.missions.frontier_loop import MissionFrontierLoop
from devintel.missions.store import Mission, MissionStatus


class FakeExecutiveBridge:
    def __init__(self, mission): self.mission = mission
    def continue_due(self, **kwargs): return (self.mission,)


def mission(status=MissionStatus.SUCCEEDED):
    now = datetime.now(timezone.utc).isoformat()
    return Mission("m1", "s", "first", 1, 1, status, 1, 3, 0.0, now, now)


def test_verified_terminal_mission_becomes_learning_and_next_mission():
    from devintel.missions.store import MissionStore
    store = MissionStore()
    learning = MissionLearningBridge(store=LearningStore(), learner=OutcomeLearner(min_samples=1, min_confidence=.5))
    loop = MissionFrontierLoop(store, FakeExecutiveBridge(mission()), learning)
    result = loop.run_once(now=0.0, candidates=(ObjectiveCandidate("next", "second", "s", "verified-outcome", .2),))
    assert result.learned_outcomes[0].verified
    assert result.next_mission is not None
    assert result.next_mission.objective == "second"


def test_failed_mission_does_not_create_learning_or_next_mission():
    from devintel.missions.store import MissionStore
    store = MissionStore()
    learning_store = LearningStore()
    learning = MissionLearningBridge(store=learning_store, learner=OutcomeLearner(min_samples=1, min_confidence=.5))
    loop = MissionFrontierLoop(store, FakeExecutiveBridge(mission(MissionStatus.FAILED)), learning)
    result = loop.run_once(now=0.0, candidates=(ObjectiveCandidate("next", "second", "s", "gap", .2),))
    assert result.learned_outcomes == ()
    assert result.next_mission is None
    assert learning_store.outcomes("s") == ()


def test_next_mission_materialization_is_idempotent():
    from devintel.missions.store import MissionStore
    store = MissionStore()
    learning = MissionLearningBridge(store=LearningStore(), learner=OutcomeLearner(min_samples=1, min_confidence=.5))
    loop = MissionFrontierLoop(store, FakeExecutiveBridge(mission()), learning)
    candidate = ObjectiveCandidate("next", "second", "s", "gap", .2)
    first = loop.run_once(now=0.0, candidates=(candidate,)).next_mission
    second = loop.run_once(now=0.0, candidates=(candidate,)).next_mission
    assert first is not None and second is not None
    assert first.mission_id == second.mission_id
