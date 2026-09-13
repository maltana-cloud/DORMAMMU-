"""Protected cryptographic authorization for emergency recovery.

The recovery key is deliberately supplied from an external secret store (the
process environment by default). It is never persisted in DORMAMMU state,
intelligence memory, audit records, or repository files.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import os
import secrets
import time


class RecoveryAuthorizationError(RuntimeError):
    """Raised when an emergency recovery request cannot be authenticated."""


@dataclass(frozen=True)
class RecoveryRequest:
    """A signed, bounded recovery authorization request."""

    scope: str
    nonce: str
    issued_at: int
    signature: str


class CryptographicRecovery:
    """Verify owner recovery requests without granting normal authority.

    HMAC-SHA256 is used because this project intentionally has no third-party
    crypto dependency. The secret must be provisioned outside the repository.
    For multi-operator deployments, a future asymmetric provider can implement
    the same boundary without changing the security orchestrator contract.
    """

    def __init__(self, secret: bytes | None = None, *, max_age_seconds: int = 300) -> None:
        if max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")
        self._secret = secret if secret is not None else self._load_secret()
        if len(self._secret) < 32:
            raise ValueError("recovery secret must contain at least 32 bytes")
        self.max_age_seconds = max_age_seconds
        self._used_nonces: set[str] = set()

    @staticmethod
    def _load_secret() -> bytes:
        encoded = os.environ.get("DORMAMMU_RECOVERY_SECRET")
        if not encoded:
            raise RecoveryAuthorizationError("DORMAMMU_RECOVERY_SECRET is not configured")
        try:
            value = bytes.fromhex(encoded)
        except ValueError as exc:
            raise RecoveryAuthorizationError("recovery secret must be hex encoded") from exc
        return value

    @staticmethod
    def generate_secret() -> str:
        """Generate a repository-safe value for external secret provisioning."""
        return secrets.token_hex(32)

    @staticmethod
    def _payload(scope: str, nonce: str, issued_at: int) -> bytes:
        if not scope.strip() or not nonce.strip():
            raise ValueError("scope and nonce are required")
        return f"DORMAMMU-RECOVERY-V1|{scope}|{nonce}|{issued_at}".encode("utf-8")

    def sign(self, scope: str, nonce: str, issued_at: int | None = None) -> RecoveryRequest:
        """Create a request for an authorized external recovery operator."""
        timestamp = int(time.time()) if issued_at is None else int(issued_at)
        payload = self._payload(scope, nonce, timestamp)
        signature = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return RecoveryRequest(scope, nonce, timestamp, signature)

    def verify(self, request: RecoveryRequest, *, now: int | None = None) -> None:
        """Verify authenticity, freshness, and single-use nonce semantics."""
        current = int(time.time()) if now is None else int(now)
        if abs(current - request.issued_at) > self.max_age_seconds:
            raise RecoveryAuthorizationError("recovery request is expired")
        if request.nonce in self._used_nonces:
            raise RecoveryAuthorizationError("recovery request nonce has already been used")
        expected = hmac.new(
            self._secret,
            self._payload(request.scope, request.nonce, request.issued_at),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, request.signature):
            raise RecoveryAuthorizationError("invalid recovery authorization")
        self._used_nonces.add(request.nonce)
