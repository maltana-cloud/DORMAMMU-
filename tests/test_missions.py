import pytest

from devintel.missions import MissionRunner, MissionRunPolicy, MissionStatus, MissionStore


def test_mission_is_durable_and_resumable(tmp_path):
    path = tmp_path / "missions.db"
    store = MissionStore(str(path))
    mission = store.create("research", "complete investigation", total_steps=3, now=10)
    assert mission.current_step == 0

    calls = []
    runner = MissionRunner(store)
    first = runner.run_once(now=10, step=lambda current: calls.append(current.current_step), policy=MissionRunPolicy(max_steps=1))
    assert first[0].status is MissionStatus.QUEUED
    assert first[0].current_step == 1
    store.close()

    reopened = MissionStore(str(path))
    runner = MissionRunner(reopened)
    second = runner.run_once(now=11, step=lambda current: None, policy=MissionRunPolicy(max_steps=2))
    assert second[-1].status is MissionStatus.SUCCEEDED
    assert second[-1].current_step == 3
    reopened.close()


def test_failed_steps_retry_then_terminal_failure():
    store = MissionStore()
    mission = store.create("scope", "fragile work", total_steps=1, max_attempts=2, now=0)
    runner = MissionRunner(store)
    first = runner.run_once(now=0, step=lambda _: (_ for _ in ()).throw(RuntimeError("boom")), policy=MissionRunPolicy(max_steps=1, retry_backoff_seconds=5))
    assert first[0].status is MissionStatus.QUEUED
    assert first[0].next_run_at == 5

    second = runner.run_once(now=5, step=lambda _: (_ for _ in ()).throw(RuntimeError("boom")), policy=MissionRunPolicy(max_steps=1))
    assert second[0].status is MissionStatus.FAILED
    assert second[0].attempts == 2
    store.close()


def test_pause_resume_and_cancel_are_explicit():
    store = MissionStore()
    mission = store.create("scope", "controlled work", total_steps=2, now=0)
    runner = MissionRunner(store)
    running = store.claim_due(now=0)
    assert running is not None
    paused = runner.pause(mission.mission_id)
    assert paused.status is MissionStatus.PAUSED
    resumed = runner.resume(mission.mission_id, now=2)
    assert resumed.status is MissionStatus.QUEUED
    cancelled = runner.cancel(mission.mission_id)
    assert cancelled.status is MissionStatus.CANCELLED
    with pytest.raises(ValueError):
        runner.cancel(mission.mission_id)
    store.close()


def test_run_is_bounded_by_max_steps():
    store = MissionStore()
    mission = store.create("scope", "bounded work", total_steps=10, now=0)
    runner = MissionRunner(store)
    result = runner.run_once(now=0, step=lambda _: None, policy=MissionRunPolicy(max_steps=2))
    assert len(result) == 2
    assert result[-1].current_step == 2
    assert result[-1].status is MissionStatus.QUEUED
    store.close()


def test_invalid_bounds_and_inputs_fail_closed():
    with pytest.raises(ValueError):
        MissionStore().create("scope", "objective", 0)
    with pytest.raises(ValueError):
        MissionRunPolicy(max_steps=0)
    with pytest.raises(TypeError):
        MissionRunner(MissionStore()).run_once(now=0, step="not-callable")
