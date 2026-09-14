from devintel.modules.creative import AssetKind, CreativeBrief, CreativeProvider
from devintel.runtime.app import DORMAMMURuntime


def test_runtime_exposes_bounded_creative_pipeline():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_creative_provider(CreativeProvider("local", "Local", (AssetKind.VIDEO,), approved=True, trust_score=.8))
        result = runtime.creative_plan(CreativeBrief("teach", "learners", AssetKind.VIDEO))
        assert result.plan.status.value == "ready_for_creation"
        assert result.provider.provider_id == "local"
        assert result.artifact.artifact_digest
    finally:
        runtime.close()
