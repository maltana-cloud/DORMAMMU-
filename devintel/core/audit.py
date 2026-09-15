"""Structured, bounded audit records with tamper-evident chaining."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class AuditRecord:
    event: str
    action: str = ""
    success: bool | None = None
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog:
    """Bounded, thread-safe audit trail with an independently verifiable chain."""

    def __init__(self, history_limit: int = 2000) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self._records: list[AuditRecord] = []
        self._digests: list[str] = []
        self._anchor_digest = "GENESIS"
        self._limit = history_limit
        self._lock = RLock()

    @staticmethod
    def _canonical(entry: AuditRecord, previous_digest: str) -> bytes:
        payload = {
            "event": entry.event,
            "action": entry.action,
            "success": entry.success,
            "details": entry.details,
            "created_at": entry.created_at.isoformat(),
            "previous_digest": previous_digest,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")

    def record(self, entry: AuditRecord) -> AuditRecord:
        with self._lock:
            previous = self._digests[-1] if self._digests else self._anchor_digest
            digest = hashlib.sha256(self._canonical(entry, previous)).hexdigest()
            self._records.append(entry)
            self._digests.append(digest)
            if len(self._records) > self._limit:
                removed = len(self._records) - self._limit
                self._anchor_digest = self._digests[removed - 1]
                del self._records[:removed]
                del self._digests[:removed]
        return entry

    def history(self) -> tuple[AuditRecord, ...]:
        with self._lock:
            return tuple(self._records)

    def verify_integrity(self) -> bool:
        """Verify the retained history without exposing internal digests."""
        with self._lock:
            previous = self._anchor_digest
            for entry, stored in zip(self._records, self._digests):
                expected = hashlib.sha256(self._canonical(entry, previous)).hexdigest()
                if expected != stored:
                    return False
                previous = stored
            return True
