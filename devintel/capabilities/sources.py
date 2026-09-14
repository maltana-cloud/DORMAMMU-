"""Durable, explicitly trusted configuration for external capability catalogs."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from urllib.parse import urlparse

from .catalog import CatalogPolicy, HttpJsonCatalogScout
from .discovery import DiscoveryPolicy


@dataclass(frozen=True)
class CapabilitySourceConfig:
    source_id: str
    endpoint: str
    publisher: str
    trusted_source: str
    terms_url: str = ""
    enabled: bool = False
    timeout_seconds: float = 5.0
    max_bytes: int = 1_000_000

    def __post_init__(self) -> None:
        for value, name in ((self.source_id, "source_id"), (self.endpoint, "endpoint"), (self.publisher, "publisher"), (self.trusted_source, "trusted_source")):
            if not value.strip():
                raise ValueError(f"{name} is required")
        parsed = urlparse(self.endpoint)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("endpoint must use HTTPS")
        if self.terms_url:
            terms = urlparse(self.terms_url)
            if terms.scheme != "https" or not terms.hostname:
                raise ValueError("terms_url must use HTTPS")
        CatalogPolicy(self.timeout_seconds, self.max_bytes, (parsed.hostname,))


class CapabilitySourceStore:
    """SQLite source registry. Configuration never implies trust or execution."""
    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("""CREATE TABLE IF NOT EXISTS capability_sources (
            source_id TEXT PRIMARY KEY, endpoint TEXT NOT NULL, publisher TEXT NOT NULL,
            trusted_source TEXT NOT NULL, terms_url TEXT NOT NULL, enabled INTEGER NOT NULL,
            timeout_seconds REAL NOT NULL, max_bytes INTEGER NOT NULL)""")
        self._db.commit()

    def upsert(self, config: CapabilitySourceConfig) -> None:
        self._db.execute("""INSERT INTO capability_sources VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET endpoint=excluded.endpoint,
            publisher=excluded.publisher, trusted_source=excluded.trusted_source,
            terms_url=excluded.terms_url, enabled=excluded.enabled,
            timeout_seconds=excluded.timeout_seconds, max_bytes=excluded.max_bytes""",
            (config.source_id, config.endpoint, config.publisher, config.trusted_source,
             config.terms_url, int(config.enabled), config.timeout_seconds, config.max_bytes))
        self._db.commit()

    def get(self, source_id: str) -> CapabilitySourceConfig:
        row = self._db.execute("SELECT * FROM capability_sources WHERE source_id=?", (source_id,)).fetchone()
        if row is None:
            raise KeyError(source_id)
        return CapabilitySourceConfig(row[0], row[1], row[2], row[3], row[4], bool(row[5]), row[6], row[7])

    def enabled(self) -> tuple[CapabilitySourceConfig, ...]:
        rows = self._db.execute("SELECT * FROM capability_sources WHERE enabled=1 ORDER BY source_id").fetchall()
        return tuple(CapabilitySourceConfig(r[0], r[1], r[2], r[3], r[4], True, r[6], r[7]) for r in rows)

    def close(self) -> None:
        self._db.close()


class ConfiguredCapabilitySource:
    """Build a bounded HTTPS scout only from an explicitly enabled source."""
    def __init__(self, config: CapabilitySourceConfig, *, discovery_policy: DiscoveryPolicy) -> None:
        if not config.enabled:
            raise PermissionError("capability source is disabled")
        if config.trusted_source not in discovery_policy.trusted_evidence_sources:
            raise PermissionError("source is not trusted by the active discovery policy")
        parsed = urlparse(config.endpoint)
        self.config = config
        self.scout = HttpJsonCatalogScout(
            config.endpoint, source=config.trusted_source, publisher=config.publisher,
            policy=CatalogPolicy(config.timeout_seconds, config.max_bytes, (parsed.hostname,)),
        )

    def discover(self, requirement):
        return self.scout.discover(requirement)
