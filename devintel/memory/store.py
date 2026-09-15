"""Bounded durable memory with provenance, confidence, freshness, and revision."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import sqlite3
from typing import Sequence


class MemoryKind(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    ENTITY = "entity"
    MISSION = "mission"
    REFLECTION = "reflection"


@dataclass(frozen=True)
class MemoryEntry:
    memory_id: str
    scope_id: str
    kind: MemoryKind
    subject: str
    content: str
    evidence_refs: tuple[str, ...] = ()
    confidence: float = 0.0
    observed_at: datetime = datetime.min.replace(tzinfo=timezone.utc)
    expires_at: datetime | None = None
    revision: int = 1
    supersedes: str | None = None
    active: bool = True

    def __post_init__(self) -> None:
        for value, name in ((self.memory_id, "memory_id"), (self.scope_id, "scope_id"), (self.subject, "subject"), (self.content, "content")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.kind, MemoryKind):
            raise TypeError("kind must be MemoryKind")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.observed_at.tzinfo is None or (self.expires_at is not None and self.expires_at.tzinfo is None):
            raise ValueError("memory timestamps must be timezone-aware")
        if self.revision <= 0:
            raise ValueError("revision must be positive")
        if len(self.evidence_refs) > 64:
            raise ValueError("too many evidence references")


class MemoryStore:
    """SQLite-backed memory; stored content is data, never authority or executable instructions."""

    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS memories (
            memory_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, kind TEXT NOT NULL,
            subject TEXT NOT NULL, content TEXT NOT NULL, evidence_refs TEXT NOT NULL,
            confidence REAL NOT NULL, observed_at TEXT NOT NULL, expires_at TEXT,
            revision INTEGER NOT NULL, supersedes TEXT, active INTEGER NOT NULL,
            CHECK(confidence >= 0 AND confidence <= 1), CHECK(revision > 0)
        )""")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_memories_scope_active ON memories(scope_id, active, observed_at DESC)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_memories_subject ON memories(scope_id, subject, revision DESC)")
        self.connection.commit()

    @staticmethod
    def deterministic_id(scope_id: str, kind: MemoryKind, subject: str, content: str) -> str:
        payload = f"DORMAMMU-MEMORY-V1|{scope_id}|{kind.value}|{subject}|{content}".encode()
        return hashlib.sha256(payload).hexdigest()

    def remember(self, entry: MemoryEntry) -> MemoryEntry:
        self.connection.execute(
            "INSERT OR REPLACE INTO memories(memory_id,scope_id,kind,subject,content,evidence_refs,confidence,observed_at,expires_at,revision,supersedes,active) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (entry.memory_id, entry.scope_id, entry.kind.value, entry.subject, entry.content, json.dumps(entry.evidence_refs), entry.confidence, entry.observed_at.isoformat(), entry.expires_at.isoformat() if entry.expires_at else None, entry.revision, entry.supersedes, int(entry.active)),
        )
        self.connection.commit()
        return entry

    def revise(self, previous_id: str, entry: MemoryEntry) -> MemoryEntry:
        previous = self.get(previous_id)
        if previous is None:
            raise KeyError(previous_id)
        if previous.scope_id != entry.scope_id or previous.subject != entry.subject:
            raise ValueError("revisions must remain in the same scope and subject")
        if entry.revision <= previous.revision:
            raise ValueError("revision must increase")
        self.connection.execute("UPDATE memories SET active=0 WHERE memory_id=?", (previous_id,))
        self.remember(MemoryEntry(entry.memory_id, entry.scope_id, entry.kind, entry.subject, entry.content, entry.evidence_refs, entry.confidence, entry.observed_at, entry.expires_at, entry.revision, previous_id, entry.active))
        return entry

    def get(self, memory_id: str) -> MemoryEntry | None:
        row = self.connection.execute("SELECT memory_id,scope_id,kind,subject,content,evidence_refs,confidence,observed_at,expires_at,revision,supersedes,active FROM memories WHERE memory_id=?", (memory_id,)).fetchone()
        return self._entry(row) if row else None

    def recall(self, scope_id: str, *, query: str = "", kinds: Sequence[MemoryKind] = (), limit: int = 100, now: datetime | None = None) -> tuple[MemoryEntry, ...]:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        if limit <= 0 or limit > 1000: raise ValueError("limit must be between 1 and 1000")
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None: raise ValueError("now must be timezone-aware")
        sql = "SELECT memory_id,scope_id,kind,subject,content,evidence_refs,confidence,observed_at,expires_at,revision,supersedes,active FROM memories WHERE scope_id=? AND active=1 AND (expires_at IS NULL OR expires_at>?)"
        args: list[object] = [scope_id, current.isoformat()]
        if kinds:
            sql += " AND kind IN (" + ",".join("?" for _ in kinds) + ")"
            args.extend(kind.value for kind in kinds)
        if query:
            sql += " AND (subject LIKE ? OR content LIKE ?)"
            needle = f"%{query}%"
            args.extend((needle, needle))
        sql += " ORDER BY observed_at DESC, memory_id ASC LIMIT ?"
        args.append(limit)
        return tuple(self._entry(row) for row in self.connection.execute(sql, args).fetchall())

    def count(self, scope_id: str, *, active_only: bool = True) -> int:
        clause = " AND active=1" if active_only else ""
        return int(self.connection.execute(f"SELECT COUNT(*) FROM memories WHERE scope_id=?{clause}", (scope_id,)).fetchone()[0])

    @staticmethod
    def _entry(row: tuple[object, ...]) -> MemoryEntry:
        from datetime import datetime
        return MemoryEntry(row[0], row[1], MemoryKind(row[2]), row[3], row[4], tuple(json.loads(row[5])), float(row[6]), datetime.fromisoformat(row[7]), datetime.fromisoformat(row[8]) if row[8] else None, int(row[9]), row[10], bool(row[11]))

    def close(self) -> None:
        self.connection.close()
