"""Evidence-backed problem and opportunity discovery.

This layer converts verified synthesis signals into bounded, advisory
problem/opportunity candidates. It never grants authority or executes action.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..modules.research.synthesis import SynthesisResult, SynthesisSignal
from ..modules.research.normalization import normalize_text


@dataclass(frozen=True)
class ProblemOpportunityCandidate:
    """A ranked advisory candidate derived from a verified synthesis signal."""

    kind: str
    statement: str
    score: float
    confidence: float
    evidence_urls: tuple[str, ...]
    uncertain: bool

    def __post_init__(self) -> None:
        if self.kind not in {"problem", "opportunity"}:
            raise ValueError("kind must be problem or opportunity")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("statement is required")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0 and 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.uncertain and self.confidence > 0.49:
            raise ValueError("uncertain candidates cannot have high confidence")


@dataclass(frozen=True)
class ProblemOpportunityResult:
    topic: str
    candidates: tuple[ProblemOpportunityCandidate, ...]
    excluded: int
    uncertainty: str


class ProblemOpportunityEngine:
    """Detect unmet needs and potential opportunities without inventing facts."""

    def __init__(self, *, max_candidates: int = 50) -> None:
        if max_candidates <= 0:
            raise ValueError("max_candidates must be positive")
        self.max_candidates = max_candidates

    def identify(
        self,
        synthesis: SynthesisResult,
        *,
        limit: int = 20,
        problem_terms: Sequence[str] = ("need", "problem", "gap", "lack", "difficult", "struggling", "pain"),
        opportunity_terms: Sequence[str] = ("opportunity", "demand", "market", "available", "potential", "unmet"),
    ) -> ProblemOpportunityResult:
        if not isinstance(synthesis, SynthesisResult):
            raise TypeError("synthesis must be a SynthesisResult")
        if limit <= 0 or limit > self.max_candidates:
            raise ValueError("limit is outside the configured bound")
        problem = self._terms(problem_terms)
        opportunity = self._terms(opportunity_terms)
        candidates: list[ProblemOpportunityCandidate] = []
        excluded = synthesis.excluded_claims
        for signal in synthesis.signals:
            statement = normalize_text(signal.statement)
            if not statement:
                excluded += 1
                continue
            text = statement.lower()
            if any(term in text for term in problem):
                kind = "problem"
            elif any(term in text for term in opportunity):
                kind = "opportunity"
            else:
                excluded += 1
                continue
            evidence_factor = min(1.0, len(signal.evidence_urls) / 3.0)
            score = min(1.0, round(signal.confidence * 0.65 + evidence_factor * 0.20 + signal.uncertain * 0.0 + 0.15, 4))
            confidence = min(signal.confidence, 0.49) if signal.uncertain else signal.confidence
            candidates.append(ProblemOpportunityCandidate(kind, statement, score, confidence, signal.evidence_urls, signal.uncertain))
        candidates.sort(key=lambda item: (-item.score, -item.confidence, item.kind, item.statement))
        bounded = tuple(candidates[:limit])
        if len(candidates) > limit:
            excluded += len(candidates) - limit
        if synthesis.contradictions:
            uncertainty = "high: contradictory verified evidence requires resolution before high-confidence opportunity use"
        elif not bounded:
            uncertainty = "high: no evidence-backed problem or opportunity candidates identified"
        elif any(candidate.uncertain for candidate in bounded):
            uncertainty = "moderate: candidates include unresolved uncertainty"
        else:
            uncertainty = "bounded: candidates derive from verified synthesis with preserved provenance"
        return ProblemOpportunityResult(synthesis.topic, bounded, excluded, uncertainty)

    @staticmethod
    def _terms(values: Sequence[str]) -> tuple[str, ...]:
        if not isinstance(values, (tuple, list)):
            raise TypeError("terms must be a sequence")
        normalized = tuple(sorted({normalize_text(value).lower() for value in values if normalize_text(value)}))
        if not normalized:
            raise ValueError("at least one detection term is required")
        return normalized
