"""Durable audit trail for controlled evolution candidates and promotions."""
from __future__ import annotations
import json
import sqlite3
from .evolution import ImprovementCandidate, EvolutionEvaluation, Promotion

class EvolutionStore:
    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS evolution_candidates (
            candidate_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, target TEXT NOT NULL,
            adjustment TEXT NOT NULL, basis_cycle_ids TEXT NOT NULL, expected_delta REAL NOT NULL,
            confidence REAL NOT NULL, parent_version INTEGER NOT NULL, created_at TEXT NOT NULL
        )""")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS evolution_evaluations (
            candidate_id TEXT PRIMARY KEY, safe INTEGER NOT NULL, baseline_metric REAL NOT NULL,
            candidate_metric REAL NOT NULL, confidence REAL NOT NULL, evidence_count INTEGER NOT NULL,
            reason TEXT NOT NULL, evaluated_at TEXT NOT NULL
        )""")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS evolution_promotions (
            candidate_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, version INTEGER NOT NULL,
            parent_version INTEGER NOT NULL, promoted_at TEXT NOT NULL
        )""")
        self.connection.commit()

    def record_candidate(self, candidate: ImprovementCandidate) -> None:
        self.connection.execute("INSERT INTO evolution_candidates VALUES (?,?,?,?,?,?,?,?,?)", (candidate.candidate_id, candidate.scope_id, candidate.target, candidate.adjustment, json.dumps(candidate.basis_cycle_ids), candidate.expected_delta, candidate.confidence, candidate.parent_version, candidate.created_at.isoformat()))
        self.connection.commit()

    def record_evaluation(self, evaluation: EvolutionEvaluation) -> None:
        self.connection.execute("INSERT OR REPLACE INTO evolution_evaluations VALUES (?,?,?,?,?,?,?,?)", (evaluation.candidate_id, int(evaluation.safe), evaluation.baseline_metric, evaluation.candidate_metric, evaluation.confidence, evaluation.evidence_count, evaluation.reason, evaluation.evaluated_at.isoformat()))
        self.connection.commit()

    def record_promotion(self, promotion: Promotion) -> None:
        self.connection.execute("INSERT INTO evolution_promotions VALUES (?,?,?,?,?)", (promotion.candidate_id, promotion.scope_id, promotion.version, promotion.parent_version, promotion.promoted_at.isoformat()))
        self.connection.commit()

    def promotions(self, scope_id: str, limit: int = 100) -> tuple[Promotion, ...]:
        if not scope_id.strip() or limit <= 0:
            raise ValueError("scope_id and positive limit are required")
        rows = self.connection.execute("SELECT candidate_id,scope_id,version,parent_version,promoted_at FROM evolution_promotions WHERE scope_id=? ORDER BY version DESC LIMIT ?", (scope_id, limit)).fetchall()
        from datetime import datetime
        return tuple(Promotion(r[0], r[1], r[2], r[3], datetime.fromisoformat(r[4])) for r in rows)

    def close(self) -> None:
        self.connection.close()
