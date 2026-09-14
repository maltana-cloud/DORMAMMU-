"""Creative workflow orchestration without external side effects."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from .contracts import CreativeBrief, CreativeEvaluation, CreativePlan, CreativeStatus, brief_digest, plan_digest
from .intelligence import CreativeIntelligence
from .lineage import CreativeLineageRecord, CreativeLineageStore
from .providers import CreativeProviderRegistry, ProviderSelection
from .verification import CreativeSafetyGate, CreativeVerification, CreativeVerifier

@dataclass(frozen=True)
class CreativeArtifact:
    artifact_digest: str; plan_digest: str; revision: int; specification: str; parent_digest: str | None = None
@dataclass(frozen=True)
class CreativeResult:
    brief: CreativeBrief; plan: CreativePlan; evaluation: CreativeEvaluation; verification: CreativeVerification; artifact: CreativeArtifact; provider: ProviderSelection

class CreativePipeline:
    """Runs bounded purpose/design/create-spec/critique/repair/verify/finish steps."""
    def __init__(self, intelligence: CreativeIntelligence | None = None, providers: CreativeProviderRegistry | None = None, lineage: CreativeLineageStore | None = None, verifier: CreativeVerifier | None = None, safety: CreativeSafetyGate | None = None) -> None:
        self.intelligence = intelligence or CreativeIntelligence(); self.providers = providers or CreativeProviderRegistry(); self.lineage = lineage or CreativeLineageStore(); self.verifier = verifier or CreativeVerifier(); self.safety = safety or CreativeSafetyGate()
    def run(self, brief: CreativeBrief, *, criteria: tuple[str, ...] | None = None, max_revisions: int = 2) -> CreativeResult:
        if not 0 <= max_revisions <= 8: raise ValueError("max_revisions must be between 0 and 8")
        safe, safety_reasons = self.safety.assess(brief)
        plan = self.intelligence.plan(brief); evaluation = self.intelligence.critique(plan, criteria); revision = 0; parent_digest = None
        while evaluation.status is not CreativeStatus.ACCEPTED and revision < max_revisions:
            parent_digest = plan_digest(plan); plan = self.intelligence.revise(plan, evaluation); evaluation = self.intelligence.critique(plan, criteria); revision += 1
        verification = self.verifier.verify(brief, plan)
        if not safe:
            verification = CreativeVerification(verification.plan_digest, False, verification.score, verification.checks, verification.defects + safety_reasons, True)
        digest = plan_digest(plan); specification = "\n".join((plan.concept, *plan.steps)); artifact_digest = sha256(f"{digest}\n{revision}\n{specification}".encode("utf-8")).hexdigest()
        artifact = CreativeArtifact(artifact_digest, digest, revision, specification, parent_digest)
        self.lineage.record(CreativeLineageRecord(artifact_digest, digest, brief_digest(brief), brief.evidence_refs, revision, self.lineage.now()))
        return CreativeResult(brief, plan, evaluation, verification, artifact, self.providers.select(brief.asset_kind))
    def close(self) -> None:
        self.lineage.close()
