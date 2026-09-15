from devintel.modules.community import (
    CommunityContent, CommunityIntelligence, CommunityMember, CommunityPolicy, CommunityRuntimeAdapter,
    ContentKind, MemberKind, SignalKind,
)

def sample():
    members = (CommunityMember("u1", MemberKind.PERSON, "A", True), CommunityMember("u2", MemberKind.PERSON, "B"))
    content = (
        CommunityContent("c1", "u1", ContentKind.POST, "How do I solve this problem?", ("python",), ("source:c1",)),
        CommunityContent("c2", "u2", ContentKind.COMMENT, "There is a hiring opportunity available.", (), ("source:c2",)),
    )
    return members, content

def test_observation_analysis_and_plan_are_bounded_and_deterministic():
    members, content = sample(); engine = CommunityIntelligence()
    obs = engine.observe("community-1", members, content)
    plan1 = engine.plan(obs); plan2 = engine.plan(obs)
    assert plan1 == plan2
    assert plan1.signals[0].kind in {SignalKind.QUESTION, SignalKind.OPPORTUNITY}
    assert plan1.drafts

def test_unknown_author_fails_closed():
    members, _ = sample(); engine = CommunityIntelligence()
    bad = (CommunityContent("c1", "unknown", ContentKind.POST, "hello"),)
    try: engine.observe("c", members, bad)
    except ValueError as exc: assert "author" in str(exc)
    else: raise AssertionError("unknown author must fail")

def test_policy_requires_authorized_owner_for_publication():
    members, content = sample(); signal = CommunityIntelligence().analyze(CommunityIntelligence().observe("c", members, content))[0]
    policy = CommunityPolicy()
    assert not policy.evaluate(signal, publish=True).allowed
    assert not policy.evaluate(signal, publish=True, platform_authorized=True).allowed
    assert policy.evaluate(signal, publish=True, platform_authorized=True, owner_approved=True).allowed

def test_risk_without_evidence_is_rejected():
    from devintel.modules.community import CommunitySignal
    signal = CommunitySignal("c", "x", SignalKind.RISK, "risk", 1.0, 1.0, ())
    assert not CommunityPolicy().evaluate(signal).allowed

def test_store_persists_and_limits_history():
    members, content = sample(); adapter = CommunityRuntimeAdapter()
    run = adapter.analyze("c", members, content)
    assert run.stored_plan_id
    assert adapter.store.history("c", 1)
    adapter.close()

def test_no_external_publish_transport_exists_in_runtime_adapter():
    assert not hasattr(CommunityRuntimeAdapter, "publish")

def test_text_and_tag_bounds():
    from devintel.modules.community.contracts import normalize_text, normalize_tags
    assert normalize_text(" a   b ") == "a b"
    try: normalize_text("x" * 4097)
    except ValueError: pass
    else: raise AssertionError("oversized text must fail")
    assert normalize_tags(("Python", "python")) == ("python",)
