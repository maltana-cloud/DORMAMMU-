"""Bounded conversion of discovered problems/opportunities into mission proposals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .problem_opportunity import ProblemOpportunityCandidate, ProblemOpportunityResult
from ..missions.store import Mission, MissionStep, MissionStore


@dataclass(frozen=True)
class MissionProposal:
    """Advisory mission proposal; creation does not grant execution authority."""

    proposal_id: str
    kind: str
    objective: str
    scope_id: str
    evidence_urls: tuple[str, ...]
    confidence: float


class GapMissionEngine:
    """Create deterministic, bounded mission proposals from verified discovery signals."""

    def __init__(self, *, max_proposals: int = 16) -> None:
        if max_proposals <= 0:
            raise ValueError("max_proposals must be positive")
        self.max_proposals = max_proposals

    def propose(self, result: ProblemOpportunityResult, *, scope_id: str) -> tuple[MissionProposal, ...]:
        if not isinstance(result, ProblemOpportunityResult):
            raise TypeError("result must be a ProblemOpportunityResult")
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        proposals: list[MissionProposal] = []
        for candidate in result.candidates:
            if candidate.uncertain or candidate.confidence < 0.5:
                continue
            proposal_id = f"{candidate.kind}:{candidate.statement.lower()}"
            proposals.append(
                MissionProposal(
                    proposal_id=proposal_id,
                    kind=candidate.kind,
                    objective=candidate.statement,
                    scope_id=scope_id.strip(),
                    evidence_urls=candidate.evidence_urls,
                    confidence=candidate.confidence,
                )
            )
        proposals.sort(key=lambda p: (-p.confidence, p.kind, p.objective, p.proposal_id))
        return tuple(proposals[: self.max_proposals])

    def materialize(
        self,
        store: MissionStore,
        proposal: MissionProposal,
        *,
        now: float = 0.0,
        max_attempts: int = 3,
    ) -> Mission:
        if not isinstance(proposal, MissionProposal):
            raise TypeError("proposal must be a MissionProposal")
        mission_id = self._mission_id(proposal)
        existing = store.get(mission_id)
        if existing is not None:
            return existing
        mission = store.create(proposal.scope_id, proposal.objective, 1, max_attempts=max_attempts, mission_id=mission_id, now=now)
        store.define_steps(
            mission.mission_id,
            (MissionStep(
                "discoverable-gap",
                proposal.objective,
                {"intent": proposal.objective, "desired_outcome": f"Produce a verified result for: {proposal.objective}"},
            ),),
        )
        return store.get(mission.mission_id)  # type: ignore[return-value]

    @staticmethod
    def _mission_id(proposal: MissionProposal) -> str:
        import hashlib
        return "gap-" + hashlib.sha256(proposal.proposal_id.encode("utf-8")).hexdigest()[:32]
