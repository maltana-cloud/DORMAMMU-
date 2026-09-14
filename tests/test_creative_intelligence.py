import pytest

from devintel.modules.creative import (
    AssetKind,
    CreativeBrief,
    CreativeIntelligence,
    CreativeStatus,
    brief_digest,
    plan_digest,
)


def make_brief():
    return CreativeBrief(
        purpose="Explain a complex idea clearly",
        audience="general learners",
        asset_kind=AssetKind.VIDEO,
        constraints=("respect copyright", "protect privacy"),
        success_criteria=("clear", "useful"),
    )


def test_plan_is_bounded_and_deterministic():
    engine = CreativeIntelligence()
    first = engine.plan(make_brief())
    second = engine.plan(make_brief())
    assert first == second
    assert first.status is CreativeStatus.READY_FOR_CREATION
    assert first.brief_digest == brief_digest(make_brief())
    assert plan_digest(first)


def test_critique_accepts_complete_plan():
    engine = CreativeIntelligence()
    plan = engine.plan(make_brief())
    result = engine.critique(plan)
    assert result.status is CreativeStatus.ACCEPTED
    assert result.plan_digest == plan_digest(plan)
    assert result.defects == ()


def test_revision_requires_matching_evaluation():
    engine = CreativeIntelligence()
    plan = engine.plan(make_brief())
    evaluation = engine.critique(plan)
    assert engine.revise(plan, evaluation) == plan
    with pytest.raises(ValueError):
        engine.revise(plan, engine.critique(engine.plan(CreativeBrief("x", "y", AssetKind.TEXT))))


def test_input_bounds_fail_closed():
    with pytest.raises(ValueError):
        CreativeBrief("", "audience", AssetKind.TEXT)
    with pytest.raises(ValueError):
        CreativeBrief("x" * 16385, "audience", AssetKind.TEXT)


def test_creative_layer_has_no_execution_authority_surface():
    import devintel.modules.creative as creative
    assert not hasattr(creative.CreativeIntelligence, "execute")
    assert not hasattr(creative.CreativeIntelligence, "publish")
    assert not hasattr(creative.CreativeIntelligence, "spend")
