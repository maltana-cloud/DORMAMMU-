from devintel.modules.creative import AssetKind, CreativeBrief, CreativeProvider
from devintel.runtime.app import DORMAMMURuntime

def test_runtime_exposes_bounded_creative_pipeline_and_lineage():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_creative_provider(CreativeProvider("local", "Local", (AssetKind.VIDEO,), approved=True, trust_score=.8))
        result = runtime.creative_plan(CreativeBrief("teach", "learners", AssetKind.VIDEO, evidence_refs=("claim:1",)))
        assert result.plan.status.value == "ready_for_creation" and result.provider.provider_id == "local" and result.artifact.artifact_digest
        record = runtime.creative.lineage.get(result.artifact.artifact_digest)
        assert record is not None and record.evidence_refs == ("claim:1",) and record.plan_digest == result.artifact.plan_digest
    finally:
        runtime.close()
