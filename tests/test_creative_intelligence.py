import pytest
from devintel.modules.creative import AssetKind, CreativeBrief, CreativeConsistency, CreativeIntelligence, CreativePipeline, CreativeProvider, CreativeProviderRegistry, CreativeStatus, brief_digest, plan_digest

def make_brief(): return CreativeBrief("Explain a complex idea clearly", "general learners", AssetKind.VIDEO, ("respect copyright", "protect privacy"), ("clear", "useful"), ("evidence:claim-1",))
def test_plan_is_bounded_deterministic_and_evidence_bound():
    engine=CreativeIntelligence(); first=engine.plan(make_brief()); assert first==engine.plan(make_brief()); assert first.status is CreativeStatus.READY_FOR_CREATION; assert first.brief_digest==brief_digest(make_brief()); assert plan_digest(first); assert first.brief_digest != brief_digest(CreativeBrief("Explain a complex idea clearly","general learners",AssetKind.VIDEO))
def test_ideation_and_variations_are_bounded_and_distinct():
    engine=CreativeIntelligence(); concepts=engine.ideate(make_brief(),count=4); variants=engine.variations(concepts[0],count=4); assert len(concepts)==4 and len({c.title for c in concepts})==4; assert len(variants)==4 and len({c.title for c in variants})==4
    with pytest.raises(ValueError): engine.ideate(make_brief(),count=17)
def test_critique_and_revision():
    engine=CreativeIntelligence(); plan=engine.plan(make_brief()); result=engine.critique(plan); assert result.status is CreativeStatus.ACCEPTED and result.plan_digest==plan_digest(plan) and result.defects==(); bad=engine.critique(engine.plan(CreativeBrief("x","y",AssetKind.TEXT)))
    with pytest.raises(ValueError): engine.revise(plan,bad)
def test_custom_weak_criterion_can_be_repaired_but_remains_truthful():
    engine=CreativeIntelligence(); plan=engine.plan(make_brief()); evaluation=engine.critique(plan,("unknown",)); assert evaluation.status is CreativeStatus.NEEDS_REVIEW and evaluation.defects; assert engine.revise(plan,evaluation).status is CreativeStatus.READY_FOR_CREATION
def test_consistency_is_validated_and_bound_to_plan_digest():
    consistency=CreativeConsistency("cinematic","hero-1","forest","1920x1080",24,"16:9","stable",("color-grade",)); plan=CreativeIntelligence().plan(make_brief(),consistency=consistency); assert plan.consistency==consistency and plan_digest(plan)!=brief_digest(make_brief())
    with pytest.raises(ValueError): CreativeConsistency("x"*16385)
    with pytest.raises(ValueError): CreativeConsistency(fps=241)
def test_provider_selection_fails_closed_and_prefers_trust_with_fallbacks():
    registry=CreativeProviderRegistry([CreativeProvider("low","Low",(AssetKind.VIDEO,),approved=True,trust_score=.4),CreativeProvider("high","High",(AssetKind.VIDEO,),approved=True,trust_score=.9),CreativeProvider("blocked","Blocked",(AssetKind.VIDEO,),approved=False,trust_score=1.0)]); selection=registry.select(AssetKind.VIDEO); assert selection.provider_id=="high" and selection.fallback_provider_ids==("low",); assert registry.select(AssetKind.IMAGE).provider_id is None
    limited=CreativeProviderRegistry([CreativeProvider("small","Small",(AssetKind.VIDEO,),max_resolution=(1280,720),approved=True,trust_score=1.0)]); assert limited.select(AssetKind.VIDEO,(1920,1080)).provider_id is None
    with pytest.raises(ValueError): limited.select(AssetKind.VIDEO,(0,1080))
def test_pipeline_binds_artifact_to_plan_and_has_no_external_side_effects():
    provider=CreativeProvider("local","Local",(AssetKind.VIDEO,),approved=True,trust_score=.8); result=CreativePipeline(providers=CreativeProviderRegistry([provider])).run(make_brief()); assert result.evaluation.status is CreativeStatus.ACCEPTED and result.provider.provider_id=="local"; assert result.artifact.plan_digest==plan_digest(result.plan); assert result.artifact.artifact_digest

def test_input_and_provider_bounds_fail_closed():
    with pytest.raises(ValueError): CreativeBrief("","audience",AssetKind.TEXT)
    with pytest.raises(ValueError): CreativeBrief("x"*16385,"audience",AssetKind.TEXT)
    with pytest.raises(ValueError): CreativeProvider("x","x",(AssetKind.TEXT,),trust_score=1.1)
    with pytest.raises(ValueError): CreativePipeline().run(make_brief(),max_revisions=9)
def test_creative_layer_has_no_execution_authority_surface():
    from devintel.modules.creative import CreativeIntelligence
    assert not hasattr(CreativeIntelligence,"execute"); assert not hasattr(CreativeIntelligence,"publish"); assert not hasattr(CreativeIntelligence,"spend")
