"""Conservative bridge from verified knowledge synthesis to executive cognition."""
from __future__ import annotations

from dataclasses import dataclass

from ..modules.research import SynthesisResult
from .contracts import GoalUnderstanding, Objective


class EvidenceRequirementError(ValueError):
    """Raised when synthesized evidence cannot safely drive executive planning."""


@dataclass(frozen=True)
class EvidenceBackedUnderstanding:
    """Executive understanding plus the evidence boundary that produced it."""

    understanding: GoalUnderstanding
    source_topic: str
    provenance: tuple[str, ...]
    uncertainty: str


class EvidenceBackedExecutiveAdapter:
    """Convert only eligible synthesis signals into explicit executive criteria.

    This adapter never upgrades evidence into authority. Contradictory or
    low-confidence signals are excluded by ``executive_requirements()`` and
    remain visible through the returned synthesis metadata.
    """

    def understand(
        self,
        objective: Objective,
        synthesis: SynthesisResult,
    ) -> EvidenceBackedUnderstanding:
        if not isinstance(objective, Objective):
            raise TypeError("objective must be an Objective")
        if not isinstance(synthesis, SynthesisResult):
            raise TypeError("synthesis must be a SynthesisResult")

        requirements = synthesis.executive_requirements()
        if not requirements:
            raise EvidenceRequirementError(
                "synthesis contains no sufficiently confident, non-contradictory executive requirements"
            )

        constraints = dict(objective.constraints)
        constraints["evidence_topic"] = synthesis.topic
        constraints["evidence_uncertainty"] = synthesis.uncertainty
        understanding = GoalUnderstanding(
            objective=objective,
            normalized_goal=" ".join(objective.intent.split()),
            success_criteria=tuple(requirements),
            constraints=constraints,
            evidence_urls=synthesis.provenance,
            evidence_topic=synthesis.topic,
            evidence_uncertainty=synthesis.uncertainty,
        )
        return EvidenceBackedUnderstanding(
            understanding=understanding,
            source_topic=synthesis.topic,
            provenance=synthesis.provenance,
            uncertainty=synthesis.uncertainty,
        )
