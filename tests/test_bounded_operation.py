from devintel.capabilities import CapabilityDescriptor, CapabilityRequirement, CapabilityStatus, CanaryHealth
from devintel.core.contracts import ActionRequest, ActionRisk
from devintel.operations import BoundedOperation, BoundedOperationEngine
from devintel.runtime.app import DORMAMMURuntime


class Scout:
    def discover(self, requirement):
        return (
            CapabilityDescriptor(
                "test.echo",
                "Test echo",
                "1.0",
                ("echo",),
                "trusted-test",
                "internal",
                permissions=("approved",),
                metadata={"performance": "good"},
            ),
        )


def test_existing_capability_runs_through_action_and_verification():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_action("test.echo", lambda payload: {"echo": payload["value"]})
        operation = BoundedOperation(
            "echo a value",
            CapabilityRequirement("runtime-local", "run locally", ("runtime",)),
            ActionRequest("test.echo", ActionRisk.LOW, "bounded test action", {"value": "ok"}),
        )
        result = BoundedOperationEngine(runtime).run(operation, verifier=lambda output: output == {"echo": "ok"})
        assert result.success
        assert result.verified
        assert result.stage == "record"
        assert result.action_result is not None and result.action_result.success
        names = [event.name for event in runtime.context.events.history()]
        assert names[0] == "operation.requested"
        assert "operation.completed" in names
        assert names[-1] == "operation.recorded"
    finally:
        runtime.close()


def test_high_risk_action_stops_at_permission_boundary():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_action("test.high", lambda payload: {"ok": True})
        operation = BoundedOperation(
            "perform protected work",
            CapabilityRequirement("runtime-local", "run locally", ("runtime",)),
            ActionRequest("test.high", ActionRisk.HIGH, "protected test action"),
        )
        result = BoundedOperationEngine(runtime).run(operation, verifier=lambda _: True)
        assert not result.success
        assert result.stage == "act"
        assert result.action_result is not None
        assert not result.action_result.success
    finally:
        runtime.close()


def test_missing_capability_requires_approval_then_canary_before_action():
    runtime = DORMAMMURuntime()
    try:
        runtime.capability_discovery.add_scout(Scout())
        runtime.register_action("test.echo", lambda payload: payload)
        operation = BoundedOperation(
            "use discovered echo capability",
            CapabilityRequirement("echo-capability", "echo values", ("echo",)),
            ActionRequest("test.echo", ActionRisk.LOW, "echo through candidate", {"value": 7}),
        )
        engine = BoundedOperationEngine(runtime)
        blocked = engine.run(operation)
        assert not blocked.success and blocked.stage == "approval"

        result = engine.run(
            operation,
            capability_approved=True,
            canary_health=CanaryHealth(True, 1.0, 0.0, 10.0),
            verifier=lambda output: output == {"value": 7},
        )
        assert result.success and result.verified
        assert runtime.capability_registry.get("test.echo").status is CapabilityStatus.ACTIVE
        history = runtime.lifecycle_history("test.echo")
        assert [event.to_status for event in history] == [
            CapabilityStatus.EVALUATED,
            CapabilityStatus.APPROVED,
            CapabilityStatus.REGISTERED,
            CapabilityStatus.CANARY,
            CapabilityStatus.ACTIVE,
        ]
    finally:
        runtime.close()


def test_failed_verification_is_recorded_as_failure():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_action("test.echo", lambda payload: payload)
        operation = BoundedOperation(
            "echo with failing verifier",
            CapabilityRequirement("runtime-local", "run locally", ("runtime",)),
            ActionRequest("test.echo", ActionRisk.LOW, "verification test", {"value": 1}),
        )
        result = BoundedOperationEngine(runtime).run(operation, verifier=lambda _: False)
        assert not result.success
        assert result.stage == "verify"
        assert not result.verified
        assert any(event.name == "operation.verification_failed" for event in runtime.context.events.history())
    finally:
        runtime.close()
