"""Bounded orchestration from completed missions into learning and one next mission."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from collections.abc import Sequence
from datetime import datetime, timezone
from ..autonomy.learning import OutcomeEvidence
from ..autonomy.mission_learning import MissionLearningBridge
from ..autonomy.next_objective import ObjectiveCandidate
from ..intelligence.gap_missions import MissionProposal
from .executive_bridge import MissionExecutiveBridge, MissionExecutionPolicy
from .store import Mission, MissionStep, MissionStore

@dataclass(frozen=True)
class FrontierLoopResult:
    completed_missions: tuple[Mission, ...]
    learned_outcomes: tuple[OutcomeEvidence, ...]
    next_mission: Mission | None

class MissionFrontierLoop:
    """Run one bounded execution pass, learn only from verified terminal missions, and materialize at most one next mission."""
    def __init__(self, store: MissionStore, executive_bridge: MissionExecutiveBridge, learning_bridge: MissionLearningBridge, *, max_new_missions: int = 1) -> None:
        if max_new_missions != 1: raise ValueError("max_new_missions must be exactly 1")
        self.store, self.executive_bridge, self.learning_bridge = store, executive_bridge, learning_bridge

    def run_once(self, *, now: float, candidates: Sequence[ObjectiveCandidate] = (), scope_id: str | None = None, worker_id: str | None = None, policy: MissionExecutionPolicy | None = None) -> FrontierLoopResult:
        missions = self.executive_bridge.continue_due(now=now, scope_id=scope_id, worker_id=worker_id, policy=policy)
        learned: list[OutcomeEvidence] = []
        next_mission: Mission | None = None
        for mission in missions:
            if mission.status.value != "succeeded": continue
            evidence = OutcomeEvidence(mission.scope_id, mission.mission_id, True, True, 1.0, "mission reached a verified terminal state", datetime.now(timezone.utc), mission.mission_id)
            transition = self.learning_bridge.transition(evidence, candidates)
            learned.append(evidence)
            if transition.next_objective is not None:
                next_mission = self._materialize_next(transition.next_objective.candidate)
                break
        return FrontierLoopResult(tuple(missions), tuple(learned), next_mission)

    def _materialize_next(self, candidate: ObjectiveCandidate) -> Mission:
        mission_id = "learned-" + sha256(candidate.objective_id.encode("utf-8")).hexdigest()[:32]
        existing = self.store.get(mission_id)
        if existing is not None: return existing
        mission = self.store.create(candidate.scope_id, candidate.objective, 1, mission_id=mission_id)
        self.store.define_steps(mission.mission_id, (MissionStep("learned-next", candidate.objective, {"intent": candidate.objective, "desired_outcome": f"Produce a verified result for: {candidate.objective}"}),))
        return self.store.get(mission_id)  # type: ignore[return-value]
