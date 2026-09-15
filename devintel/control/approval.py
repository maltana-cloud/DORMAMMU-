"""Authenticated, scoped owner-approval tokens for protected control commands."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import os
import secrets
import time

from .contracts import ControlCommand


class ApprovalAuthorizationError(RuntimeError):
    """Raised when an owner approval cannot be authenticated safely."""


@dataclass(frozen=True)
class OwnerApproval:
    command_id: str
    scope_id: str
    nonce: str
    issued_at: int
    signature: str


class OwnerApprovalAuthority:
    """Issue and verify short-lived, single-use approvals outside normal policy."""

    def __init__(self, secret: bytes | None = None, *, max_age_seconds: int = 300) -> None:
        if max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")
        self._secret = secret if secret is not None else self._load_secret()
        if len(self._secret) < 32:
            raise ValueError("owner approval secret must contain at least 32 bytes")
        self.max_age_seconds = max_age_seconds
        self._used_nonces: set[str] = set()

    @staticmethod
    def _load_secret() -> bytes:
        encoded = os.environ.get("DORMAMMU_OWNER_APPROVAL_SECRET")
        if not encoded:
            raise ApprovalAuthorizationError("DORMAMMU_OWNER_APPROVAL_SECRET is not configured")
        try:
            return bytes.fromhex(encoded)
        except ValueError as exc:
            raise ApprovalAuthorizationError("owner approval secret must be hex encoded") from exc

    @staticmethod
    def generate_secret() -> str:
        return secrets.token_hex(32)

    @staticmethod
    def _payload(command_id: str, scope_id: str, nonce: str, issued_at: int) -> bytes:
        if not command_id.strip() or not scope_id.strip() or not nonce.strip():
            raise ValueError("command_id, scope_id, and nonce are required")
        return f"DORMAMMU-OWNER-APPROVAL-V1|{command_id}|{scope_id}|{nonce}|{issued_at}".encode()

    def approve(self, command: ControlCommand, issued_at: int | None = None) -> OwnerApproval:
        timestamp = int(time.time()) if issued_at is None else int(issued_at)
        nonce = secrets.token_hex(16)
        payload = self._payload(command.command_id, command.scope_id, nonce, timestamp)
        signature = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return OwnerApproval(command.command_id, command.scope_id, nonce, timestamp, signature)

    def verify(self, command: ControlCommand, approval: OwnerApproval, *, now: int | None = None) -> None:
        current = int(time.time()) if now is None else int(now)
        if approval.command_id != command.command_id or approval.scope_id != command.scope_id:
            raise ApprovalAuthorizationError("owner approval scope or command mismatch")
        if abs(current - approval.issued_at) > self.max_age_seconds:
            raise ApprovalAuthorizationError("owner approval is expired")
        if approval.nonce in self._used_nonces:
            raise ApprovalAuthorizationError("owner approval nonce has already been used")
        expected = hmac.new(
            self._secret,
            self._payload(approval.command_id, approval.scope_id, approval.nonce, approval.issued_at),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, approval.signature):
            raise ApprovalAuthorizationError("invalid owner approval")
        self._used_nonces.add(approval.nonce)
