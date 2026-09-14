from devintel.modules.creative import AssetKind, CreativeBrief, CreativeContextAdapter

def test_context_uses_language_and_preserves_bounded_operating_knowledge():
    brief = CreativeBrief("Create an explanation", "learners", AssetKind.VIDEO, evidence_refs=("claim:1",))
    context = CreativeContextAdapter().build(brief, scope_id="scope-1", known_capabilities=("creative.intelligence",), known_resources=("gpu.local",), known_limits=("no publishing",))
    assert context.brief_digest and context.language.intents == ("creation",) and context.cognition is None
    assert context.capability_ids == ("creative.intelligence",) and context.resource_ids == ("gpu.local",)
