"""Deterministic quality and safety checks for creative specifications."""
from __future__ import annotations
from dataclasses import dataclass
from .contracts import CreativeBrief, CreativePlan, CreativeStatus, plan_digest

_BLOCKED_ACTION_WORDS = frozenset({"pay", "purchase", "transfer", "withdraw", "publish", "deploy", "send", "delete", "impersonate", "bypass"})

@dataclass(frozen=True)
class CreativeVerification:
    plan_digest: str
    passed: bool
    score: float
    checks: tuple[tuple[str, bool], ...]
    defects: tuple[str, ...]
    requires_review: bool

class CreativeVerifier:
    """Verify structure and safety without claiming that generated media is true or good."""
    def verify(self, brief: CreativeBrief, plan: CreativePlan) -> CreativeVerification:
        if plan.brief_digest != self._brief_digest(brief):
            raise ValueError("plan does not match the supplied brief")
        checks = (
            ("purpose", bool(brief.purpose.strip() and brief.purpose.strip() in plan.concept or "success:" in plan.concept.lower())),
            ("audience", "audience" in " ".join(plan.steps).lower()),
            ("constraints", len(brief.constraints) == 0 or any("constraint" in step.lower() for step in plan.steps)),
            ("consistency", bool(plan.consistency.seed_strategy)),
            ("verification", any("verification" in step.lower() for step in plan.steps)),
            ("reviewability", plan.status is CreativeStatus.READY_FOR_CREATION),
            ("bounded_plan", 1 <= len(plan.steps) <= 64),
        )
        defects = tuple(f"verification failed: {name}" for name, ok in checks if not ok)
        text = " ".join((brief.purpose, brief.audience, *brief.constraints, *brief.success_criteria)).casefold()
        blocked = tuple(sorted(word for word in _BLOCKED_ACTION_WORDS if word in text))
        if blocked:
            defects += ("high-impact external action language requires authorization: " + ", ".join(blocked),)
        score = sum(ok for _, ok in checks) / len(checks)
        return CreativeVerification(plan_digest(plan), not defects and score >= 0.85, score, checks, defects, bool(blocked) or bool(defects))

    @staticmethod
    def _brief_digest(brief: CreativeBrief) -> str:
        from .contracts import brief_digest
        return brief_digest(brief)

class CreativeSafetyGate:
    """Classify creative requests that must remain review-gated."""
    def assess(self, brief: CreativeBrief) -> tuple[bool, tuple[str, ...]]:
        text = " ".join((brief.purpose, brief.audience, *brief.constraints)).casefold()
        reasons = tuple(f"review required for restricted action term: {word}" for word in sorted(_BLOCKED_ACTION_WORDS) if word in text)
        return not reasons, reasons
