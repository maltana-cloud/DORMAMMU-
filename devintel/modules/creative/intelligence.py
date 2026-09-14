"""Bounded creative intelligence: brief -> plan -> critique."""
from __future__ import annotations

from .contracts import CreativeBrief, CreativeEvaluation, CreativePlan, CreativeStatus, brief_digest, plan_digest


class CreativeIntelligence:
    """Create deterministic creative plans and evaluate them without executing them."""

    def plan(self, brief: CreativeBrief) -> CreativePlan:
        digest = brief_digest(brief)
        steps = (
            "clarify purpose and audience",
            "develop a primary concept",
            "define the asset structure and production requirements",
            "identify quality criteria and likely failure modes",
            "prepare a reviewable creation specification",
        )
        risks = tuple(c for c in brief.constraints if any(word in c.lower() for word in ("legal", "copyright", "privacy", "safety", "brand")))
        return CreativePlan(
            brief_digest=digest,
            concept=f"Create a {brief.asset_kind.value} that serves {brief.audience.strip()} by achieving: {', '.join(brief.success_criteria) or brief.purpose.strip()}",
            steps=steps,
            risks=risks,
            status=CreativeStatus.READY_FOR_CREATION,
        )

    def critique(self, plan: CreativePlan, criteria: tuple[str, ...] | None = None) -> CreativeEvaluation:
        selected = criteria or ("purpose", "audience", "coherence", "constraints", "reviewability")
        scores: list[tuple[str, float]] = []
        defects: list[str] = []
        for criterion in selected[:64]:
            key = criterion.strip().lower()
            if key == "purpose": score = 1.0
            elif key == "audience": score = 1.0 if "audience" in " ".join(plan.steps).lower() else 0.5
            elif key == "coherence": score = 1.0 if len(plan.steps) >= 3 else 0.5
            elif key == "constraints": score = 1.0 if plan.risks or not plan.risks else 0.8
            elif key == "reviewability": score = 1.0 if plan.status == CreativeStatus.READY_FOR_CREATION else 0.6
            else: score = 0.5
            scores.append((criterion, score))
            if score < 0.7:
                defects.append(f"criterion below acceptance threshold: {criterion}")
        status = CreativeStatus.ACCEPTED if scores and min(score for _, score in scores) >= 0.7 else CreativeStatus.NEEDS_REVIEW
        return CreativeEvaluation(plan_digest=plan_digest(plan), criterion_scores=tuple(scores), defects=tuple(defects), status=status)

    def revise(self, plan: CreativePlan, evaluation: CreativeEvaluation) -> CreativePlan:
        if evaluation.plan_digest != plan_digest(plan):
            raise ValueError("evaluation does not match the supplied plan")
        if evaluation.status == CreativeStatus.ACCEPTED:
            return plan
        extra = tuple(f"repair defect: {d}" for d in evaluation.defects[:16])
        return CreativePlan(
            brief_digest=plan.brief_digest,
            concept=plan.concept,
            steps=plan.steps + extra,
            risks=plan.risks,
            status=CreativeStatus.READY_FOR_CREATION,
        )
