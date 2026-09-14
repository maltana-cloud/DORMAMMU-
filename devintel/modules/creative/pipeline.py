"""Creative workflow orchestration without external side effects."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .contracts import CreativeBrief, CreativeEvaluation, CreativePlan, CreativeStatus, plan_digest
from .intelligence import CreativeIntelligence
from .providers import CreativeProviderRegistry, ProviderSelection


@dataclass(frozen=True)
class CreativeArtifact:
    artifact_digest: str
    plan_digest: str
    revision: int
    specification: str
    parent_digest: str | None = None


@dataclass(frozen=True)
class CreativeResult:
    brief: CreativeBrief
    plan: CreativePlan
    evaluation: CreativeEvaluation
    artifact: CreativeArtifact
    provider: ProviderSelection


class CreativePipeline:
    """Runs purpose/design/critique/repair/verify/finish as pure bounded steps."""

    def __init__(self, intelligence: CreativeIntelligence | None = None, providers: CreativeProviderRegistry | None = None) -> None:
        self.intelligence = intelligence or CreativeIntelligence()
        self.providers = providers or CreativeProviderRegistry()

    def run(self, brief: CreativeBrief, *, criteria: tuple[str, ...] | None = None, max_revisions: int = 2) -> CreativeResult:
        if not 0 <= max_revisions <= 8:
            raise ValueError("max_revisions must be between 0 and 8")
        plan = self.intelligence.plan(brief)
        evaluation = self.intelligence.critique(plan, criteria)
        revision = 0
        while evaluation.status is not CreativeStatus.ACCEPTED and revision < max_revisions:
            plan = self.intelligence.revise(plan, evaluation)
            evaluation = self.intelligence.critique(plan, criteria)
            revision += 1
        if evaluation.status is not CreativeStatus.ACCEPTED:
            status_plan = CreativePlan(plan.brief_digest, plan.concept, plan.steps, plan.risks, CreativeStatus.NEEDS_REVIEW)
            plan = status_plan
            evaluation = self.intelligence.critique(plan, criteria)
        digest = plan_digest(plan)
        specification = "\n".join((plan.concept, *plan.steps))
        artifact_digest = sha256(f"{digest}\n{revision}\n{specification}".encode("utf-8")).hexdigest()
        artifact = CreativeArtifact(artifact_digest, digest, revision, specification)
        return CreativeResult(brief, plan, evaluation, artifact, self.providers.select(brief.asset_kind))
