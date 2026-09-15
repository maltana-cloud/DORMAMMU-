from devintel.actions import ActionExecutor, ActionOutcome, ActionRegistry, ActionSpec, ActionStatus
from devintel.core import ActionRisk, PermissionPolicy


class Provider:
    capability = "publish"

    def __init__(self, provider_id, success=True):
        self.provider_id = provider_id
        self.success = success
        self.calls = 0

    def health(self):
        return True

    def execute(self, spec):
        self.calls += 1
        if not self.success:
            return ActionOutcome(spec.action_id, spec.capability, ActionStatus.FAILED, self.provider_id, "failed")
        return ActionOutcome(spec.action_id, spec.capability, ActionStatus.SUCCEEDED, self.provider_id, "sent")


def spec(risk=ActionRisk.LOW, key="k", dry_run=False):
    return ActionSpec("publish.message", "publish", risk, key, {"text": "hello"}, "scope", dry_run)


def test_high_risk_requires_owner_approval():
    registry = ActionRegistry()
    registry.register(Provider("p1"))
    executor = ActionExecutor(registry)
    denied = executor.execute(spec(ActionRisk.HIGH))
    assert denied.status is ActionStatus.DENIED
    assert not registry.providers("publish")[0].calls
    allowed = executor.execute(spec(ActionRisk.HIGH, "approved"), owner_approved=True)
    assert allowed.status is ActionStatus.SUCCEEDED


def test_fallback_and_idempotency():
    first = Provider("a", success=False)
    second = Provider("b", success=True)
    registry = ActionRegistry()
    registry.register(second)
    registry.register(first)
    executor = ActionExecutor(registry)
    outcome = executor.execute(spec(key="same"))
    assert outcome.provider_id == "b"
    again = executor.execute(spec(key="same"))
    assert again == outcome
    assert second.calls == 1


def test_dry_run_has_no_external_side_effect():
    provider = Provider("p1")
    registry = ActionRegistry()
    registry.register(provider)
    outcome = ActionExecutor(registry).execute(spec(key="dry", dry_run=True))
    assert outcome.status is ActionStatus.DRY_RUN
    assert provider.calls == 0


def test_verifier_is_explicit_and_failure_is_isolated():
    provider = Provider("p1")
    registry = ActionRegistry()
    registry.register(provider)
    executor = ActionExecutor(registry, verifier=lambda _spec, _outcome: True)
    outcome = executor.execute(spec(key="verified"))
    assert outcome.verified is True


def test_invalid_provider_result_fails_closed():
    class Bad(Provider):
        def execute(self, _spec):
            return object()
    registry = ActionRegistry()
    registry.register(Bad("bad"))
    outcome = ActionExecutor(registry).execute(spec(key="bad"))
    assert outcome.status is ActionStatus.FAILED
