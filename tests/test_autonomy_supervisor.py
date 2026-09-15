from devintel.autonomy import (
    AutonomousEngine,
    AutonomousSupervisor,
    AutonomyRunPolicy,
    Observation,
)
from devintel.core.contracts import ActionRequest
from devintel.core.orchestrator import Orchestrator


def make_engine(calls):
    runtime = Orchestrator()
    runtime.register("ping", lambda payload: calls.append(payload) or {"ok": True})
    return AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal")],
        planner=lambda scope, observations: [
            ActionRequest("ping", reason="bounded test", payload={"_scope_id": scope})
        ],
        verifier=lambda scope, results: len(results) == 1 and results[0].success,
    )


def test_supervisor_runs_multiple_finite_cycles():
    calls = []
    run = AutonomousSupervisor(make_engine(calls)).run(
        "scope",
        policy=AutonomyRunPolicy(max_cycles=3),
    )
    assert len(run.cycles) == 3
    assert all(cycle.verified for cycle in run.cycles)
    assert run.stopped is True
    assert run.stop_reason == "cycle limit reached"
    assert len(calls) == 3


def test_supervisor_stops_on_failed_cycle():
    runtime = Orchestrator()
    runtime.register("ping", lambda payload: None)
    engine = AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal")],
        planner=lambda scope, observations: [
            ActionRequest("ping", payload={"_scope_id": scope})
        ],
        verifier=lambda scope, results: False,
    )
    run = AutonomousSupervisor(engine).run(
        "scope",
        policy=AutonomyRunPolicy(max_cycles=5, stop_on_failure=True),
    )
    assert len(run.cycles) == 1
    assert run.stopped is True
    assert "failed" in run.stop_reason


def test_supervisor_rejects_unbounded_policy_values():
    try:
        AutonomyRunPolicy(max_cycles=0)
        assert False
    except ValueError:
        pass

    try:
        AutonomyRunPolicy(max_cycles=1, max_duration_seconds=0)
        assert False
    except ValueError:
        pass
