from devintel.core.audit import AuditLog
from devintel.core.events import EventBus
from devintel.core.state import RuntimeState, StateStore
from devintel.modules.security import (
    CryptographicRecovery,
    RecoveryAuthorizationError,
    SecurityEvent,
    SecurityOrchestrator,
    SecurityState,
    ThreatLevel,
)


SECRET = b"x" * 32


def test_orchestrator_contains_high_risk_scope_and_records_audit():
    audit = AuditLog()
    events = EventBus()
    manager = SecurityOrchestrator(audit=audit, events=events)
    manager.containment.register("channel:a", {"publish", "read"})
    manager.containment.register("channel:b", {"publish"})

    result = manager.detect(SecurityEvent("prompt_injection", ThreatLevel.HIGH, "channel:a", "untrusted instruction"))

    assert result.state == SecurityState.CONTAINMENT
    assert result.capabilities_revoked == ("publish", "read")
    assert manager.containment.state("channel:b") == SecurityState.NORMAL
    assert "security.detected" in [item.name for item in events.history()]
    assert any(item.event == "security.contained" for item in audit.history())


def test_critical_scoped_detection_does_not_compromise_global_runtime():
    state = StateStore()
    orchestrator = SecurityOrchestrator(runtime_state=state)

    result = orchestrator.detect(SecurityEvent("credential_anomaly", ThreatLevel.CRITICAL, "provider:x", "unexpected use"))

    assert result.state == SecurityState.CONTAINMENT
    assert state.state == RuntimeState.NORMAL


def test_critical_core_detection_syncs_global_runtime_state():
    state = StateStore()
    orchestrator = SecurityOrchestrator(runtime_state=state)

    result = orchestrator.detect(SecurityEvent("core_anomaly", ThreatLevel.CRITICAL, "core", "foundational threat"))

    assert result.state == SecurityState.CONTAINMENT
    assert state.state == RuntimeState.CONTAINMENT


def test_recovery_and_restore_emit_auditable_events():
    audit = AuditLog()
    events = EventBus()
    recovery = CryptographicRecovery(SECRET)
    orchestrator = SecurityOrchestrator(audit=audit, events=events, recovery=recovery)
    orchestrator.detect(SecurityEvent("incident", ThreatLevel.HIGH, "channel:a", "incident"))
    request = recovery.sign("channel:a", "nonce-1", issued_at=100)
    orchestrator.begin_recovery("channel:a", request)
    record = orchestrator.restore("channel:a", ("credential revoked", "health check passed"))

    assert record.verified
    names = [event.name for event in events.history()]
    assert names[-2:] == ["security.recovery_started", "security.restored"]
    assert len(orchestrator.owner_summary()) >= 3


def test_recovery_rejects_tampered_request():
    recovery = CryptographicRecovery(SECRET)
    request = recovery.sign("core", "nonce-2", issued_at=100)
    bad = type(request)(request.scope, request.nonce, request.issued_at, "00" * 32)

    try:
        recovery.verify(bad, now=100)
    except RecoveryAuthorizationError:
        pass
    else:
        raise AssertionError("tampered recovery request must be rejected")


def test_recovery_rejects_replay():
    recovery = CryptographicRecovery(SECRET)
    request = recovery.sign("core", "nonce-3", issued_at=100)
    recovery.verify(request, now=100)

    try:
        recovery.verify(request, now=100)
    except RecoveryAuthorizationError:
        pass
    else:
        raise AssertionError("replayed recovery request must be rejected")


def test_recovery_rejects_expired_request():
    recovery = CryptographicRecovery(SECRET, max_age_seconds=5)
    request = recovery.sign("core", "nonce-4", issued_at=100)

    try:
        recovery.verify(request, now=106)
    except RecoveryAuthorizationError:
        pass
    else:
        raise AssertionError("expired recovery request must be rejected")


def test_recovery_requires_configuration():
    orchestrator = SecurityOrchestrator()
    try:
        orchestrator.begin_recovery("core", object())
    except RuntimeError:
        pass
    else:
        raise AssertionError("recovery must not operate without a cryptographic authorizer")


def test_safe_degraded_path_revokes_scope_capabilities():
    orchestrator = SecurityOrchestrator()
    orchestrator.containment.register("research", {"fetch", "store"})
    record = orchestrator.safe_degraded("research", "provider outage")

    assert record.state == SecurityState.SAFE_DEGRADED
    assert orchestrator.containment.capabilities("research") == frozenset()
