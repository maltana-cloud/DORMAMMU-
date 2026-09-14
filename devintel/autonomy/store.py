"""Durable audit-friendly storage for bounded autonomous cycles."""
from __future__ import annotations
import json
import sqlite3
from .contracts import AutonomousCycle

class AutonomousCycleStore:
    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS autonomous_cycles (
            cycle_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, completed_phases TEXT NOT NULL,
            actions_planned INTEGER NOT NULL, actions_succeeded INTEGER NOT NULL,
            actions_failed INTEGER NOT NULL, verified INTEGER NOT NULL, stopped INTEGER NOT NULL,
            stop_reason TEXT NOT NULL, improvement_actions_proposed INTEGER NOT NULL DEFAULT 0,
            recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        self.connection.commit()

    def record(self, cycle: AutonomousCycle) -> None:
        self.connection.execute(
            """INSERT INTO autonomous_cycles
            (cycle_id, scope_id, completed_phases, actions_planned, actions_succeeded,
             actions_failed, verified, stopped, stop_reason, improvement_actions_proposed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (cycle.cycle_id, cycle.scope_id, json.dumps([phase.value for phase in cycle.completed_phases]),
             cycle.actions_planned, cycle.actions_succeeded, cycle.actions_failed,
             int(cycle.verified), int(cycle.stopped), cycle.stop_reason,
             cycle.improvement_actions_proposed),
        )
        self.connection.commit()

    def history(self, scope_id: str | None = None, *, limit: int = 100) -> tuple[AutonomousCycle, ...]:
        if limit <= 0: raise ValueError("limit must be positive")
        query = "SELECT cycle_id, scope_id, completed_phases, actions_planned, actions_succeeded, actions_failed, verified, stopped, stop_reason, improvement_actions_proposed FROM autonomous_cycles"
        params: tuple[object, ...] = ()
        if scope_id is not None:
            query += " WHERE scope_id = ?"; params = (scope_id,)
        query += " ORDER BY recorded_at DESC, rowid DESC LIMIT ?"; params += (limit,)
        rows = self.connection.execute(query, params).fetchall()
        from .contracts import AutonomyPhase
        return tuple(AutonomousCycle(row[0], row[1], tuple(AutonomyPhase(p) for p in json.loads(row[2])), row[3], row[4], row[5], bool(row[6]), bool(row[7]), row[8], row[9]) for row in rows)

    def close(self) -> None:
        self.connection.close()
