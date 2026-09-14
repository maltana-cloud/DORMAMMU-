import pytest

from devintel.executive.routing import (
    RoutingRequirement,
    SpecialistDescriptor,
    SpecialistKind,
    SpecialistRouter,
)


def test_router_selects_best_eligible_specialist_deterministically():
    router = SpecialistRouter()
    router.register(SpecialistDescriptor("slow", SpecialistKind.MODEL, "provider-b", "1", ("research",), cost=5))
    router.register(SpecialistDescriptor("preferred", SpecialistKind.AGENT, "provider-a", "2", ("research",), cost=2))
    router.register(SpecialistDescriptor("unhealthy", SpecialistKind.MODEL, "provider-a", "2", ("research",), healthy=False))
    selected = router.select(RoutingRequirement("research", ("research",), preferred_provider="provider-a", preferred_version="2"))
    assert selected.specialist.specialist_id == "preferred"


def test_router_requires_all_required_skills_and_cost_limit():
    router = SpecialistRouter()
    router.register(SpecialistDescriptor("one", SpecialistKind.SPECIALIST, "p", "1", ("research",), cost=1))
    with pytest.raises(LookupError):
        router.select(RoutingRequirement("research+coding", ("research", "coding"), max_cost=2))


def test_collaboration_is_ordered_and_has_ranked_fallbacks():
    router = SpecialistRouter()
    router.register(SpecialistDescriptor("a", SpecialistKind.MODEL, "p", "1", ("research",), cost=1))
    router.register(SpecialistDescriptor("b", SpecialistKind.MODEL, "p", "1", ("research",), cost=2))
    plan = router.plan_collaboration((
        ("research", RoutingRequirement("research", ("research",))),
        ("research again", RoutingRequirement("research", ("research",))),
    ))
    assert plan.steps[0].depends_on == ()
    assert plan.steps[1].depends_on == ("step-1",)
    assert plan.fallback_by_step["step-1"] == ("b",)


def test_routing_never_selects_unapproved_or_expensive_specialist():
    router = SpecialistRouter()
    router.register(SpecialistDescriptor("approved", SpecialistKind.MODEL, "p", "1", ("coding",), cost=10))
    router.register(SpecialistDescriptor("unapproved", SpecialistKind.MODEL, "p", "1", ("coding",), cost=0, approved=False))
    with pytest.raises(LookupError):
        router.select(RoutingRequirement("coding", ("coding",), max_cost=5))
