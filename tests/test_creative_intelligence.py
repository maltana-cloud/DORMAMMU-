import pytest

from devintel.modules.creative import (
    AssetKind, CreativeBrief, CreativeIntelligence, CreativePipeline,
    CreativeProvider, CreativeProviderRegistry, CreativeStatus, brief_digest, plan_digest,
)


def make_brief():
    return CreativeBrief(
        purpose="Explain a complex idea clearly", audience="general learners", asset_kind=AssetKind.VIDEO,
        constraints=("respect copyright", "protect privacy"), success_criteria=("clear", "useful"),
        evidence_refs=("evidence:claim-1",),
    )


def test_plan_is_bounded_deterministic_and_evidence_bound():
    engine = CreativeIntelligence(); first = engine.plan(make_brief()); second = engine.plan(make_brief())
    assert first == second and first.status is CreativeStatus.READY_FOR_CREATION
    assert first.brief_digest == brief_digest(make_brief()) and plan_digest(first)
    assert first.brief_digest != brief_digest(CreativeBrief("Explain a complex idea clearly", "general learners", AssetKind.VIDEO))


def test_ideation_and_variations_are_bounded_and_distinct():
    engine = CreativeIntelligence(); concepts = engine.ideate(make_brief(), count=4)
    assert len(concepts) == 4 and len({c.title for c in concepts}) == 4
    variants = engine.variations(concepts[0], count=4)
    assert len(variants) == 4 and len({c.title for c in variants}) == 4
    with pytest.raises(ValueError): engine.ideate(make_brief(), count=17)


def test_critique_and_revision():
    engine = CreativeIntelligence(); plan = engine.plan(make_brief()); result = engine.critique(plan)
    assert result.status is CreativeStatus.ACCEPTED and result.plan_digest == plan_digest(plan) and result.defects == ()
    with pytest.raises(ValueError): engine.revise(plan, engine.critique(engine.plan(CreativeBrief("x", "y", AssetKind.TEXT))))


def test_custom_weak_criterion_can_be_repaired_but_remains_truthful():
    engine = CreativeIntelligence(); plan = engine.plan(make_brief()); evaluation = engine.critique(plan, ("unknown",))
    assert evaluation.status is CreativeStatus.NEEDS_REVIEW and evaluation.defects
    revised = engine.revise(plan, evaluation)
    assert revised.status is CreativeStatus.READY_FOR_CREATION


def test_provider_selection_fails_closed_and_prefers_trust_with_fallbacks():
    registry = CreativeProviderRegistry([
        CreativeProvider("low", "Low", (AssetKind.VIDEO,), approved=True, trust_score=0.4),
        CreativeProvider("high", "High", (AssetKind.VIDEO,), approved=True, trust_score=0.9),
        CreativeProvider("blocked", "Blocked", (AssetKind.VIDEO,), approved=False, trust_score=1.0),
    ])
    selection = registry.select(AssetKind.VIDEO)
    assert selection.provider_id == "high" and selection.fallback_provider_ids == ("low",)
    assert registry.select(AssetKind.IMAGE).provider_id is None


def test_pipeline_binds_artifact_to_plan_and_has_no_external_side_effects():
    provider = CreativeProvider("local", "Local", (AssetKind.VIDEO,), approved=True, trust_score=0.8)
    result = CreativePipeline(providers=CreativeProviderRegistry([provider])).run(make_brief())
    assert result.evaluation.status is CreativeStatus.ACCEPTED
    assert result.provider.provider_id == "local"
    assert result.artifact.plan_digest == plan_digest(result.plan)
    assert result.artifact.artifact_digest and result.artifact.parent_digest is None


def test_input_and_provider_bounds_fail_closed():
    with pytest.raises(ValueError): CreativeBrief("", "audience", AssetKind.TEXT)
    with pytest.raises(ValueError): CreativeBrief("x" * 16385, "audience", AssetKind.TEXT)
    with pytest.raises(ValueError): CreativeProvider("x", "x", (AssetKind.TEXT,), trust_score=1.1)
    with pytest.raises(ValueError): CreativePipeline().run(make_brief(), max_revisions=9)


def test_creative_layer_has_no_execution_authority_surface():
    from devintel.modules.creative import CreativeIntelligence
    assert not hasattr(CreativeIntelligence, "execute")
    assert not hasattr(CreativeIntelligence, "publish")
    assert not hasattr(CreativeIntelligence, "spend")
