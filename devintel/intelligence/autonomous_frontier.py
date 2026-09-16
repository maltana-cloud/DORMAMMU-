"""Bounded bridge from verified synthesis into executable objective proposals.

This module connects existing intelligence primitives without granting authority.
It converts verified synthesis signals into advisory problem/opportunity candidates,
then into deterministic mission proposals. Execution remains behind the existing
mission/executive authorization boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..autonomy.next_objective import ObjectiveCandidate
from ..modules.research.synthesis import SynthesisResult
from .gap_missions import GapMissionEngine, MissionProposal
from .problem_opportunity import ProblemOpportunityEngine, ProblemOpportunityResult


@dataclass(frozen=True)
class IntelligenceFrontierResult:
    """Bounded intelligence output ready for the existing mission boundary."""

    topic: str
    problems: ProblemOpportunityResult
    objective_candidates: tuple[ObjectiveCandidate, ...]
    mission_proposals: tuple[MissionProposal, ...]


class IntelligenceFrontier:
    """Connect verified synthesis -> needs/opportunities -> objectives -> missions."""

    def __init__(
        self,
        problem_engine: ProblemOpportunityEngine | None = None,
        gap_engine: GapMissionEngine | None = None,
        *,
        max_objectives: int = 16,
    ) -> None:
        if max_objectives <= 0:
            raise ValueError("max_objectives must be positive")
        self.problem_engine = problem_engine or ProblemOpportunityEngine()
        self.gap_engine = gap_engine or GapMissionEngine()
        self.max_objectives = max_objectives

    def derive(
        self,
        synthesis: SynthesisResult,
        *,
        scope_id: str,
        limit: int = 16,
    ) -> IntelligenceFrontierResult:
        if not isinstance(synthesis, SynthesisResult):
            raise TypeError("synthesis must be a SynthesisResult")
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        if limit <= 0 or limit > self.max_objectives:
            raise ValueError("limit is outside the configured bound")

        problems = self.problem_engine.identify(synthesis, limit=limit)
        candidates: list[ObjectiveCandidate] = []
        for item in problems.candidates:
            objective_id = self._objective_id(scope_id, item.kind, item.statement)
            priority = round(item.score if item.kind == "problem" else item.score * 0.95, 4)
            candidates.append(
                ObjectiveCandidate(
                    objective_id=objective_id,
                    objective=item.statement,
                    scope_id=scope_id.strip(),
                    source=f"synthesis:{item.kind}",
                    priority=priority,
                    evidence_cycle_ids=item.evidence_urls,
                )
            )
        candidates.sort(key=lambda item: (-item.priority, item.objective_id, item.objective))
        bounded = tuple(candidates[:limit])
        proposals = self.gap_engine.propose(problems, scope_id=scope_id.strip())
        return IntelligenceFrontierResult(synthesis.topic, problems, bounded, proposals)

    @staticmethod
    def _objective_id(scope_id: str, kind: str, statement: str) -> str:
        import hashlib
        payload = f"{scope_id.strip()}|{kind}|{statement.strip().lower()}".encode("utf-8")
        return "synthesis-" + hashlib.sha256(payload).hexdigest()[:32]
