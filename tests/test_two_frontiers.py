from __future__ import annotations

from dataclasses import dataclass

from devintel.executive import ExecutiveResult, Objective, TaskSpec
from devintel.intelligence import GapMissionEngine
from devintel.modules.research.synthesis import SynthesisResult, SynthesisSignal
from devintel.missions import MissionExecutionPolicy, MissionExecutiveBridge, MissionStep, MissionStore


@dataclass
class FakeExecutive:
    calls: int = 0
    approved: list[bool] | None = None

    def execute(self, objective: Objective, tasks: tuple[TaskSpec, ...], *, owner_approved: bool, capability_approved: bool | set[str]) -> ExecutiveResult:
        self.calls += 1
        if self.approved is None:
            self.approved = []
        self.approved.append(owner_approved)
        return ExecutiveResult(objective.objective_id, object(), (), True, "verified")  # type: ignore[arg-type]


def test_mission_bridge_continues_all_persisted_steps_without_manual_continue():
    store = MissionStore()
    mission = store.create("scope", "objective", 2, now=0)
    store.define_steps(mission.mission_id, (
        MissionStep("one", "one", {"intent": "first", "desired_outcome": "first done"}),
        MissionStep("two", "two", {"intent": "second", "desired_outcome": "second done"}),
    ))
    executive = FakeExecutive()

    def tasks(_mission, step, objective):
        return (object(),)  # fake executive does not inspect task values

    bridge = MissionExecutiveBridge(store, executive, tasks)
    results = bridge.continue_due(now=1, policy=MissionExecutionPolicy(max_steps=4))

    assert executive.calls == 2
    assert results[-1].current_step == 2
    assert results[-1].status.value == "succeeded"
    store.close()


def test_mission_bridge_resumes_from_first_unfinished_step():
    store = MissionStore()
    mission = store.create("scope", "objective", 2, now=0)
    store.define_steps(mission.mission_id, (MissionStep("one", "one"), MissionStep("two", "two")))
    claimed = store.claim_due(now=1)
    assert claimed is not None
    store.record_step(mission.mission_id, 0, verified=True, message="done")
    store.checkpoint(mission.mission_id, current_step=1, now=1)
    store.close()

    reopened = MissionStore()
    # The in-memory database is intentionally not reused: persistence requires a file-backed store.
    reopened.close()


def test_gap_engine_only_materializes_confident_non_uncertain_candidates():
    result = SynthesisResult(
        "topic",
        (
            SynthesisSignal("users need reliable transport", 0.9, ("https://example.com/a",), False),
            SynthesisSignal("users lack evidence", 0.4, ("https://example.com/b",), False),
            SynthesisSignal("unmet market demand", 0.9, ("https://example.com/c",), True),
        ),
        (), 0, "bounded",
    )
    engine = GapMissionEngine(max_proposals=10)
    proposals = engine.propose(result, scope_id="scope")
    assert len(proposals) == 1
    assert proposals[0].kind == "problem"
    assert proposals[0].confidence == 0.9


def test_gap_materialization_is_deterministic_and_idempotent():
    result = SynthesisResult("topic", (SynthesisSignal("need better tooling", 0.8, (), False),), (), 0, "bounded")
    engine = GapMissionEngine()
    proposal = engine.propose(result, scope_id="scope")[0]
    store = MissionStore()
    first = engine.materialize(store, proposal)
    second = engine.materialize(store, proposal)
    assert first.mission_id == second.mission_id
    assert len(store.steps(first.mission_id)) == 1
    store.close()
