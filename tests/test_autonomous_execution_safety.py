from devintel.autonomy import AutonomousEngine, Observation
from devintel.core.contracts import ActionRequest, ActionRisk
from devintel.core.orchestrator import Orchestrator


def test_permission_is_preflighted_before_any_action():
    called = []
    runtime = Orchestrator()
    runtime.register("safe", lambda payload: called.append("safe") or {"ok": True})
    runtime.register("owner_only", lambda payload: called.append("owner") or {"ok": True})
    engine = AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal")],
        planner=lambda scope, observations: [
            ActionRequest("safe", ActionRisk.LOW, "safe", {"_scope_id": scope}),
            ActionRequest("owner_only", ActionRisk.CRITICAL, "requires owner", {"_scope_id": scope}),
        ],
        verifier=lambda scope, results: False,
    )
    cycle = engine.run_once("scope")
    assert cycle.stopped is True
    assert called == []
    assert "permission" in cycle.stop_reason


def test_plan_size_is_bounded():
    runtime = Orchestrator()
    runtime.register("ping", lambda payload: {"ok": True})
    engine = AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal")],
        planner=lambda scope, observations: [ActionRequest("ping", payload={"_scope_id": scope})] * 3,
        verifier=lambda scope, results: False,
        max_actions=2,
    )
    cycle = engine.run_once("scope")
    assert cycle.stopped is True
    assert "bounded action limit" in cycle.stop_reason


def test_improvement_produces_proposals_without_mutating_authority():
    runtime = Orchestrator()
    runtime.register("ping", lambda payload: {"ok": True})
    engine = AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal")],
        planner=lambda scope, observations: [ActionRequest("ping", payload={"_scope_id": scope})],
        verifier=lambda scope, results: True,
        improver=lambda cycle: ["proposal only"],
    )
    cycle = engine.run_once("scope")
    assert cycle.improvement_actions_proposed == 1
    result = runtime.execute(ActionRequest("ping", payload={"scope_id": "scope"}))
    assert result.success is True
