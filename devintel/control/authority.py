"""Durable, owner-controlled and revocable capability authority policy."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3


class AuthorityMode(StrEnum):
    DENIED = "denied"
    APPROVAL_REQUIRED = "approval_required"
    ALLOWED = "allowed"


@dataclass(frozen=True)
class AuthorityRule:
    scope_id: str
    capability: str
    mode: AuthorityMode
    expires_at: datetime | None = None
    version: int = 1
    updated_at: datetime = datetime.min.replace(tzinfo=timezone.utc)

    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.capability.strip():
            raise ValueError("scope_id and capability are required")
        if not isinstance(self.mode, AuthorityMode):
            raise TypeError("mode must be AuthorityMode")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        if self.updated_at.tzinfo is None:
            raise ValueError("updated_at must be timezone-aware")
        if self.version <= 0:
            raise ValueError("version must be positive")


class AuthorityStore:
    """Durable owner policy. Policy is authority; memory, plans, and capabilities cannot grant it."""

    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS authority_rules (
            scope_id TEXT NOT NULL, capability TEXT NOT NULL, mode TEXT NOT NULL,
            expires_at TEXT, version INTEGER NOT NULL, updated_at TEXT NOT NULL,
            PRIMARY KEY(scope_id, capability)
        )""")
        self.connection.commit()

    def set(self, scope_id: str, capability: str, mode: AuthorityMode, *, expires_at: datetime | None = None, expected_version: int | None = None, now: datetime | None = None) -> AuthorityRule:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None: raise ValueError("now must be timezone-aware")
        existing = self.get(scope_id, capability)
        if expected_version is not None and (existing is None or existing.version != expected_version):
            raise ValueError("authority version conflict")
        version = (existing.version + 1) if existing else 1
        rule = AuthorityRule(scope_id, capability, mode, expires_at, version, current)
        self.connection.execute(
            "INSERT OR REPLACE INTO authority_rules(scope_id,capability,mode,expires_at,version,updated_at) VALUES (?,?,?,?,?,?)",
            (scope_id, capability, mode.value, expires_at.isoformat() if expires_at else None, version, current.isoformat()),
        )
        self.connection.commit()
        return rule

    def get(self, scope_id: str, capability: str) -> AuthorityRule | None:
        row = self.connection.execute("SELECT scope_id,capability,mode,expires_at,version,updated_at FROM authority_rules WHERE scope_id=? AND capability=?", (scope_id, capability)).fetchone()
        return self._rule(row) if row else None

    def decide(self, scope_id: str, capability: str, *, now: datetime | None = None) -> AuthorityMode:
        rule = self.get(scope_id, capability)
        if rule is None: return AuthorityMode.DENIED
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None: raise ValueError("now must be timezone-aware")
        if rule.expires_at is not None and rule.expires_at <= current: return AuthorityMode.DENIED
        return rule.mode

    def rules(self, scope_id: str) -> tuple[AuthorityRule, ...]:
        rows = self.connection.execute("SELECT scope_id,capability,mode,expires_at,version,updated_at FROM authority_rules WHERE scope_id=? ORDER BY capability", (scope_id,)).fetchall()
        return tuple(self._rule(row) for row in rows)

    @staticmethod
    def _rule(row: tuple[object, ...]) -> AuthorityRule:
        from datetime import datetime
        return AuthorityRule(row[0], row[1], AuthorityMode(row[2]), datetime.fromisoformat(row[3]) if row[3] else None, int(row[4]), datetime.fromisoformat(row[5]))

    def close(self) -> None:
        self.connection.close()
