import pytest
from devintel.modules.creative import AssetKind, CreativeBrief, CreativeCreationAdapter, CreativePipeline, CreativeProvider, CreativeProviderRegistry

def test_creation_adapter_builds_host_routed_request_without_execution():
    result = CreativePipeline(providers=CreativeProviderRegistry((CreativeProvider("local", "Local", (AssetKind.VIDEO,), approved=True),))).run(CreativeBrief("Explain", "learners", AssetKind.VIDEO))
    request = CreativeCreationAdapter().build(result, model="test-model")
    assert request.provider_id == "local" and request.generation.metadata["creative_plan_digest"] == result.artifact.plan_digest

def test_creation_adapter_refuses_unverified_result():
    result = CreativePipeline().run(CreativeBrief("publish this", "learners", AssetKind.TEXT))
    with pytest.raises(ValueError): CreativeCreationAdapter().build(result)
