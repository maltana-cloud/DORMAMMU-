from __future__ import annotations

from dataclasses import dataclass
from tempfile import NamedTemporaryFile

from devintel.executive import ExecutiveResult, Objective, TaskSpec
from devintel.intelligence import GapMissionEngine, ProblemOpportunityEngine
from devintel.modules.research.synthesis import SynthesisResult, SynthesisSignal
from devintel.missions import MissionExecutionPolicy, MissionExecutiveBridge, MissionStep, MissionStore


@dataclass
class FakeExecutive:
    calls: int = 0

    def execute(self, objective: Objective, tasks: tuple[TaskSpec, ...], *, owner_approved: bool, capability_approved: bool | set[str]) -> ExecutiveResult:
        self.calls += 1
        return ExecutiveResult(objective.objective_id, object(), (), True, "verified")  # type: ignore[arg-type]


def test_mission_bridge_continues_all_persisted_steps_without_manual_continue():
    store = MissionStore()
    mission = store.create("scope", "objective", 2, now=0)
    store.define_steps(mission.mission_id, (
        MissionStep("one", "one", {"intent": "first", "desired_outcome": "first done"}),
        MissionStep("two", "two", {"intent": "second", "desired_outcome": "second done"}),
    ))
    executive = FakeExecutive()
    bridge = MissionExecutiveBridge(store, executive, lambda *_: (object(),))

    results = bridge.continue_due(now=1, policy=MissionExecutionPolicy(max_steps=4))

    assert executive.calls == 2
    assert results[-1].current_step == 2
    assert results[-1].status.value == "succeeded"
    store.close()


def test_persistent_mission_resume_uses_first_unfinished_step():
    with NamedTemporaryFile(suffix=".sqlite") as handle:
        store = MissionStore(handle.name)
        mission = store.create("scope", "objective", 2, now=0)
        store.define_steps(mission.mission_id, (MissionStep("one", "one"), MissionStep("two", "two")))
        assert store.claim_due(now=1) is not None
        store.record_step(mission.mission_id, 0, verified=True, message="done")
        store.checkpoint(mission.mission_id, current_step=1, now=1)
        store.close()

        reopened = MissionStore(handle.name)
        executive = FakeExecutive()
        bridge = MissionExecutiveBridge(reopened, executive, lambda *_: (object(),))
        results = bridge.continue_due(now=2, policy=MissionExecutionPolicy(max_steps=1))
        assert executive.calls == 1
        assert results[-1].current_step == 2
        assert reopened.get(mission.mission_id).status.value == "succeeded"
        reopened.close()


def test_bridge_requires_tuple_tasks_and_fails_closed():
    store = MissionStore()
    mission = store.create("scope", "objective", 1, now=0)
    store.define_steps(mission.mission_id, (MissionStep("one", "one"),))
    bridge = MissionExecutiveBridge(store, FakeExecutive(), lambda *_: [])
    results = bridge.continue_due(now=1)
    assert results[-1].status.value == "failed"
    store.close()


def _problem_result() -> object:
    synthesis = SynthesisResult(
        "topic",
        (
            SynthesisSignal("users need reliable transport", 0.9, ("https://example.com/a",), False),
            SynthesisSignal("users lack evidence", 0.4, ("https://example.com/b",), False),
            SynthesisSignal("unmet market demand", 0.9, ("https://example.com/c",), True),
        ),
        (), 0, "bounded",
    )
    return ProblemOpportunityEngine().identify(synthesis, limit=10)


def test_gap_engine_excludes_low_confidence_and_uncertain_candidates():
    proposals = GapMissionEngine(max_proposals=10).propose(_problem_result(), scope_id="scope")
    assert len(proposals) == 1
    assert proposals[0].kind == "problem"
    assert proposals[0].confidence == 0.9


def test_gap_materialization_is_deterministic_and_idempotent():
    result = SynthesisResult("topic", (SynthesisSignal("need better tooling", 0.8, (), False),), (), 0, "bounded")
    problem_result = ProblemOpportunityEngine().identify(result, limit=10)
    proposal = GapMissionEngine().propose(problem_result, scope_id="scope")[0]
    store = MissionStore()
    first = GapMissionEngine().materialize(store, proposal)
    second = GapMissionEngine().materialize(store, proposal)
    assert first.mission_id == second.mission_id
    assert len(store.steps(first.mission_id)) == 1
    store.close()
