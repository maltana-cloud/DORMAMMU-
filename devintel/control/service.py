"""Owner-facing control center with fail-closed command handling."""
from __future__ import annotations

from threading import RLock
from uuid import uuid4
from typing import Any

from .approval import OwnerApproval, OwnerApprovalAuthority
from .contracts import ControlCommand, ControlDecision, ControlSnapshot
from .policy import OwnerControlPolicy


class OwnerControlCenter:
    """Read operational state and gate sensitive commands; never bypasses core policy."""

    def __init__(
        self,
        runtime: Any,
        policy: OwnerControlPolicy | None = None,
        approval_authority: OwnerApprovalAuthority | None = None,
    ) -> None:
        self.runtime = runtime
        self.policy = policy or OwnerControlPolicy()
        self.approval_authority = approval_authority
        self._pending: dict[str, ControlCommand] = {}
        self._lock = RLock()

    def snapshot(self, scope_id: str) -> ControlSnapshot:
        snap = self.runtime.snapshot(scope_id)
        with self._lock:
            pending = sum(1 for command in self._pending.values() if command.scope_id == scope_id)
        return ControlSnapshot(
            scope_id=scope_id,
            runtime_state=snap.runtime_state,
            monitoring_state=snap.monitoring_state,
            plugin_count=len(snap.plugin_status),
            audit_events=snap.audit_events,
            pending_approvals=pending,
        )

    def request(
        self,
        scope_id: str,
        action: str,
        *,
        reason: str = "",
        requires_owner_approval: bool = True,
    ) -> ControlCommand:
        command = ControlCommand(
            uuid4().hex,
            scope_id,
            action,
            reason,
            requires_owner_approval=requires_owner_approval,
        )
        with self._lock:
            self._pending[command.command_id] = command
        return command

    def decide(
        self,
        command: ControlCommand,
        *,
        owner_approved: bool = False,
        approval: OwnerApproval | None = None,
    ) -> ControlDecision:
        """Decide a pending command; protected commands require authenticated proof.

        ``owner_approved`` remains accepted in the call signature for source
        compatibility, but it is no longer an authorization mechanism for
        protected commands. This creates the migration boundary for callers to
        move from an untrusted boolean claim to ``OwnerApproval``.
        """
        with self._lock:
            if command.command_id not in self._pending:
                return ControlDecision.DENY
        if command.requires_owner_approval:
            if approval is None or self.approval_authority is None:
                return ControlDecision.DENY
            try:
                self.approval_authority.verify(command, approval)
            except Exception:
                return ControlDecision.DENY
            return self.policy.decide(command, owner_approved=True)
        return self.policy.decide(command, owner_approved=False)

    def consume(
        self,
        command: ControlCommand,
        *,
        owner_approved: bool = False,
        approval: OwnerApproval | None = None,
    ) -> ControlDecision:
        decision = self.decide(command, owner_approved=owner_approved, approval=approval)
        if decision is ControlDecision.ALLOW:
            with self._lock:
                self._pending.pop(command.command_id, None)
        return decision
