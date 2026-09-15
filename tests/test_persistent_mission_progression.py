import pytest

from devintel.missions.progression import PersistentMissionRunner, StepOutcome
from devintel.missions import MissionRunPolicy, MissionStatus, MissionStore
from devintel.missions.store import MissionStep


def test_progression_persists_steps_and_resumes_after_reopen(tmp_path):
    path = tmp_path / "mission.db"
    store = MissionStore(str(path))
    mission = store.create("research", "finish investigation", total_steps=3, now=0)
    runner = PersistentMissionRunner(store)
    runner.define(mission.mission_id, (
        MissionStep("observe", "observe"),
        MissionStep("research", "research", {"topic": "x"}),
        MissionStep("record", "record"),
    ))
    seen = []
    first = runner.run(now=0, execute=lambda m, s: (seen.append(s.step_id) or StepOutcome(True, True, "ok")), policy=MissionRunPolicy(max_steps=1))
    assert first[0].current_step == 1
    store.close()

    reopened = MissionStore(str(path))
    resumed = PersistentMissionRunner(reopened)
    second = resumed.run(now=1, execute=lambda m, s: (seen.append(s.step_id) or StepOutcome(True, True, "ok")), policy=MissionRunPolicy(max_steps=2))
    assert second[-1].status is MissionStatus.SUCCEEDED
    assert second[-1].current_step == 3
    assert seen == ["observe", "research", "record"]
    assert all(record.completed and record.verified for record in reopened.steps(mission.mission_id))
    reopened.close()


def test_unverified_step_never_advances_checkpoint():
    store = MissionStore()
    mission = store.create("scope", "verify me", total_steps=2, now=0)
    runner = PersistentMissionRunner(store)
    runner.define(mission.mission_id, (MissionStep("a", "a"), MissionStep("b", "b")))
    result = runner.run(now=0, execute=lambda *_: StepOutcome(True, False, "evidence missing"), policy=MissionRunPolicy(max_steps=1))
    assert result[0].status is MissionStatus.QUEUED
    assert result[0].current_step == 0
    assert result[0].last_error == "evidence missing"
    assert not store.steps(mission.mission_id)[0].completed
    store.close()


def test_failed_step_retries_and_eventually_terminal():
    store = MissionStore()
    mission = store.create("scope", "retry", total_steps=1, max_attempts=2, now=0)
    runner = PersistentMissionRunner(store)
    runner.define(mission.mission_id, (MissionStep("a", "a"),))
    execute = lambda *_: (_ for _ in ()).throw(RuntimeError("boom"))
    assert runner.run(now=0, execute=execute, policy=MissionRunPolicy(max_steps=1))[0].status is MissionStatus.QUEUED
    assert runner.run(now=1, execute=execute, policy=MissionRunPolicy(max_steps=1))[0].status is MissionStatus.FAILED
    store.close()


def test_duplicate_or_wrong_step_definitions_fail_closed():
    store = MissionStore()
    mission = store.create("scope", "bounded", total_steps=2, now=0)
    runner = PersistentMissionRunner(store)
    with pytest.raises(ValueError):
        runner.define(mission.mission_id, (MissionStep("a", "a"),))
    with pytest.raises(ValueError):
        runner.define(mission.mission_id, (MissionStep("a", "a"), MissionStep("a", "duplicate")))
    store.close()


def test_invalid_executor_output_fails_without_advancing():
    store = MissionStore()
    mission = store.create("scope", "contract", total_steps=1, now=0)
    runner = PersistentMissionRunner(store)
    runner.define(mission.mission_id, (MissionStep("a", "a"),))
    result = runner.run(now=0, execute=lambda *_: object(), policy=MissionRunPolicy(max_steps=1))
    assert result[0].status is MissionStatus.QUEUED
    assert result[0].current_step == 0
    store.close()
