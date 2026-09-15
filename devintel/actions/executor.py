"""Bounded execution facade for real-world capability adapters."""
from __future__ import annotations

from hashlib import sha256
from threading import RLock
from typing import Callable

from devintel.core.audit import AuditLog, AuditRecord
from devintel.core.contracts import ActionRequest
from devintel.core.permissions import PermissionDenied, PermissionPolicy

from .contracts import ActionOutcome, ActionSpec, ActionProvider, ActionStatus

Verifier = Callable[[ActionSpec, ActionOutcome], bool]


class ActionRegistry:
    """Host-controlled, bounded registry of explicit action providers."""

    def __init__(self, max_providers: int = 128) -> None:
        if max_providers < 1:
            raise ValueError("max_providers must be positive")
        self._max = max_providers
        self._providers: dict[tuple[str, str], ActionProvider] = {}
        self._lock = RLock()

    def register(self, provider: ActionProvider) -> None:
        provider_id = getattr(provider, "provider_id", "")
        capability = getattr(provider, "capability", "")
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id is required")
        if not isinstance(capability, str) or not capability.strip():
            raise ValueError("provider capability is required")
        if not callable(getattr(provider, "execute", None)) or not callable(getattr(provider, "health", None)):
            raise TypeError("provider must implement execute and health")
        with self._lock:
            key = (capability.strip(), provider_id.strip())
            if key not in self._providers and len(self._providers) >= self._max:
                raise RuntimeError("action provider capacity reached")
            self._providers[key] = provider

    def providers(self, capability: str) -> tuple[ActionProvider, ...]:
        if not capability.strip():
            raise ValueError("capability is required")
        with self._lock:
            values = [p for (cap, _), p in self._providers.items() if cap == capability.strip()]
        return tuple(sorted(values, key=lambda p: p.provider_id))


class ActionExecutor:
    """Execute explicit actions only after permission and provider checks.

    Idempotency is process-local and scoped to the executor instance. Providers
    must still make external side effects idempotent across process recovery.
    """

    def __init__(self, registry: ActionRegistry, *, permissions: PermissionPolicy | None = None,
                 audit: AuditLog | None = None, verifier: Verifier | None = None) -> None:
        self.registry = registry
        self.permissions = permissions or PermissionPolicy()
        self.audit = audit or AuditLog()
        self.verifier = verifier
        self._completed: dict[tuple[str, str], ActionOutcome] = {}
        self._lock = RLock()

    @staticmethod
    def fingerprint(spec: ActionSpec) -> str:
        material = f"{spec.scope_id.strip()}|{spec.capability.strip()}|{spec.action_id.strip()}|{spec.idempotency_key.strip()}"
        return sha256(material.encode("utf-8")).hexdigest()

    def execute(self, spec: ActionSpec, *, owner_approved: bool = False) -> ActionOutcome:
        request = ActionRequest(spec.action_id, spec.risk, reason="authorized action execution", payload=dict(spec.payload))
        key = (spec.scope_id.strip(), self.fingerprint(spec))
        with self._lock:
            previous = self._completed.get(key)
        if previous is not None:
            return previous

        try:
            self.permissions.check(request, owner_approved=owner_approved)
        except PermissionDenied as exc:
            outcome = ActionOutcome(spec.action_id, spec.capability, ActionStatus.DENIED, message=str(exc))
            self.audit.record(AuditRecord("action.denied", action=spec.action_id, success=False, details={"scope": spec.scope_id, "reason": str(exc)}))
            return outcome

        providers = self.registry.providers(spec.capability)
        if not providers:
            outcome = ActionOutcome(spec.action_id, spec.capability, ActionStatus.UNAVAILABLE, message="no provider available")
            self.audit.record(AuditRecord("action.unavailable", action=spec.action_id, success=False, details={"scope": spec.scope_id}))
            return outcome

        if spec.dry_run:
            outcome = ActionOutcome(spec.action_id, spec.capability, ActionStatus.DRY_RUN, message="dry-run: no external side effect")
            self.audit.record(AuditRecord("action.dry_run", action=spec.action_id, success=True, details={"scope": spec.scope_id}))
            return outcome

        last_error = "all providers unavailable"
        for provider in providers:
            try:
                if not bool(provider.health()):
                    last_error = f"provider {provider.provider_id} unhealthy"
                    continue
                outcome = provider.execute(spec)
                if not isinstance(outcome, ActionOutcome):
                    raise TypeError("provider returned invalid ActionOutcome")
                if outcome.action_id != spec.action_id or outcome.capability != spec.capability:
                    raise ValueError("provider returned mismatched action")
                if outcome.status is not ActionStatus.SUCCEEDED:
                    last_error = outcome.message or "provider reported failure"
                    continue

                try:
                    verified = bool(self.verifier(spec, outcome)) if self.verifier else False
                except Exception as exc:
                    verified = False
                    self.audit.record(AuditRecord("action.verification_failed", action=spec.action_id, success=False,
                                                   details={"scope": spec.scope_id, "provider": outcome.provider_id,
                                                            "reason": str(exc) or exc.__class__.__name__}))
                outcome = ActionOutcome(outcome.action_id, outcome.capability, outcome.status, outcome.provider_id,
                                        outcome.message, outcome.data, verified, outcome.observed_at)
                with self._lock:
                    self._completed[key] = outcome
                self.audit.record(AuditRecord("action.completed", action=spec.action_id, success=True,
                                               details={"scope": spec.scope_id, "provider": outcome.provider_id, "verified": verified}))
                return outcome
            except Exception as exc:
                last_error = str(exc) or exc.__class__.__name__
                continue

        outcome = ActionOutcome(spec.action_id, spec.capability, ActionStatus.FAILED, message=last_error)
        self.audit.record(AuditRecord("action.failed", action=spec.action_id, success=False,
                                      details={"scope": spec.scope_id, "reason": last_error}))
        return outcome
