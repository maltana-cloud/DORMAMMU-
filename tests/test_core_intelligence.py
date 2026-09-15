from devintel.core import (
    ActionRequest, ActionRisk, AuditLog, AuditRecord, EventBus, InvalidStateTransition, Orchestrator,
    PermissionDenied, RuntimeEvent, RuntimeState, StateStore,
)
from devintel.core.planner import PlanStep, Planner


def test_event_handler_failure_isolated():
    bus = EventBus(history_limit=2)
    seen = []
    bus.subscribe("x", lambda event: (_ for _ in ()).throw(RuntimeError("boom")))
    bus.subscribe("x", lambda event: seen.append(event.name))
    errors = bus.publish(RuntimeEvent("x"))
    assert len(errors) == 1
    assert seen == ["x"]


def test_state_machine_rejects_unsafe_transition():
    store = StateStore()
    try:
        store.transition(RuntimeState.RECOVERY)
    except InvalidStateTransition:
        pass
    else:
        raise AssertionError("unsafe transition was accepted")


def test_planner_rejects_duplicate_step_ids():
    planner = Planner()
    steps = [PlanStep("1", "a"), PlanStep("1", "b")]
    try:
        planner.plan("t", "goal", steps)
    except ValueError:
        return
    raise AssertionError("duplicate steps were accepted")


def test_orchestrator_executes_registered_action_and_records_events():
    runtime = Orchestrator()
    runtime.register("echo", lambda payload: payload["value"])
    result = runtime.execute(ActionRequest("echo", payload={"value": "ok"}))
    assert result.success is True
    assert result.data["output"] == "ok"
    names = [event.name for event in runtime.runtime.events.history()]
    assert names == ["action.requested", "action.authorized", "action.completed"]
    assert [entry.event for entry in runtime.audit.history()] == [
        "action.requested", "action.decided", "action.authorized", "action.completed"
    ]


def test_orchestrator_unknown_action_fails_closed():
    result = Orchestrator().execute(ActionRequest("unknown"))
    assert result.success is False
    assert "No registered handler" in result.message


def test_high_risk_can_only_run_with_explicit_owner_approval():
    runtime = Orchestrator()
    runtime.register("sensitive", lambda payload: "approved")
    denied = runtime.execute(ActionRequest("sensitive", risk=ActionRisk.HIGH))
    assert denied.success is False
    approved = runtime.execute(ActionRequest("sensitive", risk=ActionRisk.HIGH), owner_approved=True, value=1.0)
    assert approved.success is True


def test_emergency_stop_fails_closed():
    runtime = Orchestrator()
    runtime.permissions.emergency_stop = True
    try:
        runtime.authorize(ActionRequest("research"))
    except PermissionDenied:
        return
    raise AssertionError("emergency stop did not block action")


def test_plan_stops_after_first_failure():
    runtime = Orchestrator()
    runtime.register("bad", lambda payload: None)
    runtime.register("good", lambda payload: "should-not-run")
    results = runtime.plan_and_run("test", [PlanStep("1", "bad"), PlanStep("2", "good")])
    assert len(results) == 1
    assert results[0].success is False


def test_runtime_rejects_duplicate_handlers_and_invalid_metrics():
    runtime = Orchestrator()
    runtime.register("echo", lambda payload: "ok")
    try:
        runtime.register("echo", lambda payload: "again")
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate handler registration was accepted")
    try:
        runtime.runtime.increment(" ")
    except ValueError:
        pass
    else:
        raise AssertionError("blank metric name was accepted")


def test_audit_log_is_bounded_and_integrity_preserved():
    audit = AuditLog(history_limit=1)
    audit.record(AuditRecord(event="one"))
    audit.record(AuditRecord(event="two"))
    assert [record.event for record in audit.history()] == ["two"]
    assert audit.verify_integrity() is True


def test_audit_integrity_detects_record_tampering():
    audit = AuditLog()
    audit.record(AuditRecord(event="one", action="test"))
    audit._records[0] = AuditRecord(event="tampered", action="test")
    assert audit.verify_integrity() is False


def test_bounded_audit_integrity_survives_multiple_evictions():
    audit = AuditLog(history_limit=2)
    for index in range(10):
        audit.record(AuditRecord(event=f"event-{index}"))
    assert [record.event for record in audit.history()] == ["event-8", "event-9"]
    assert audit.verify_integrity() is True
