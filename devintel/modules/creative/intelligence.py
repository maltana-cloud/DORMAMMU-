"""Bounded creative intelligence: understand -> ideate -> plan -> critique -> repair."""
from __future__ import annotations
from .contracts import CreativeBrief, CreativeConcept, CreativeConsistency, CreativeEvaluation, CreativePlan, CreativeStatus, brief_digest, plan_digest

class CreativeIntelligence:
    """Deterministic creative reasoning with no external execution authority."""
    def ideate(self, brief: CreativeBrief, *, count: int = 3) -> tuple[CreativeConcept, ...]:
        if not 1 <= count <= 16: raise ValueError("count must be between 1 and 16")
        audience, purpose = brief.audience.strip(), brief.purpose.strip(); criteria = ", ".join(brief.success_criteria) or purpose
        seeds = (("Direct", f"A clear, direct {brief.asset_kind.value} focused on the core outcome: {purpose}", "clarity-first"), ("Story", f"A narrative {brief.asset_kind.value} that makes the outcome memorable for {audience}", "story-led"), ("Exploration", f"A comparative {brief.asset_kind.value} that explores multiple paths toward: {criteria}", "alternative-driven"), ("Practical", f"A practical {brief.asset_kind.value} that turns the goal into usable steps for {audience}", "action-oriented"))
        return tuple(CreativeConcept(title, premise, differentiator, tuple(brief.constraints)) for title, premise, differentiator in seeds[:count])

    def variations(self, concept: CreativeConcept, *, count: int = 3) -> tuple[CreativeConcept, ...]:
        if not 1 <= count <= 16: raise ValueError("count must be between 1 and 16")
        modes = ("minimal", "bold", "educational", "cinematic", "experimental", "practical")
        return tuple(CreativeConcept(f"{concept.title} — {modes[i % len(modes)]}", concept.premise, f"{concept.differentiator}; {modes[i % len(modes)]}", concept.required_elements) for i in range(count))

    def plan(self, brief: CreativeBrief, concept: CreativeConcept | None = None, consistency: CreativeConsistency | None = None) -> CreativePlan:
        chosen = concept or self.ideate(brief, count=1)[0]
        consistency = consistency or CreativeConsistency()
        digest = brief_digest(brief)
        steps = ("clarify purpose, audience, and success criteria", f"develop concept: {chosen.title}", "define asset structure, style, consistency requirements, and production inputs", "check constraints, rights, privacy, safety, and brand requirements", "define verification checks and acceptance thresholds", "prepare a reviewable creation specification; do not execute or publish it")
        risks = tuple(c for c in brief.constraints if any(word in c.lower() for word in ("legal", "copyright", "privacy", "safety", "brand", "licensed")))
        return CreativePlan(digest, f"{chosen.premise} Differentiator: {chosen.differentiator}. Success: {', '.join(brief.success_criteria) or brief.purpose.strip()}", steps, risks, CreativeStatus.READY_FOR_CREATION, consistency)

    def critique(self, plan: CreativePlan, criteria: tuple[str, ...] | None = None) -> CreativeEvaluation:
        selected = criteria or ("purpose", "audience", "coherence", "constraints", "consistency", "verification", "reviewability")
        scores, defects = [], []; text = " ".join((plan.concept, *plan.steps, *plan.risks)).lower(); c = plan.consistency
        for criterion in selected[:64]:
            key = criterion.strip().lower()
            if not key: continue
            if key == "purpose": score = 1.0 if "success" in text else 0.5
            elif key == "audience": score = 1.0 if "audience" in text else 0.5
            elif key == "coherence": score = 1.0 if len(plan.steps) >= 5 else 0.5
            elif key == "constraints": score = 1.0 if "constraints" in text else 0.5
            elif key == "consistency": score = 1.0 if "consistency" in text and c.seed_strategy else 0.5
            elif key == "verification": score = 1.0 if "verification" in text else 0.5
            elif key == "reviewability": score = 1.0 if plan.status == CreativeStatus.READY_FOR_CREATION else 0.6
            else: score = 0.5
            scores.append((criterion, score)); defects.extend([f"criterion below acceptance threshold: {criterion}"] if score < 0.7 else [])
        if not scores: raise ValueError("at least one non-empty criterion is required")
        return CreativeEvaluation(plan_digest(plan), tuple(scores), tuple(defects), CreativeStatus.ACCEPTED if min(score for _, score in scores) >= 0.7 else CreativeStatus.NEEDS_REVIEW)

    def revise(self, plan: CreativePlan, evaluation: CreativeEvaluation) -> CreativePlan:
        if evaluation.plan_digest != plan_digest(plan): raise ValueError("evaluation does not match the supplied plan")
        if evaluation.status == CreativeStatus.ACCEPTED: return plan
        extra = tuple(f"repair defect: {d}" for d in evaluation.defects[:16])
        return CreativePlan(plan.brief_digest, plan.concept, (plan.steps + extra)[:64], plan.risks, CreativeStatus.READY_FOR_CREATION, plan.consistency)
