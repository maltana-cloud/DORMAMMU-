from devintel.modules.community import CommunityContent, CommunityIntelligence, CommunityMember, CommunityPolicy, CommunityRuntimeAdapter, CommunitySignal, CommunitySubsystemIntegration, ContentKind, MemberKind, SignalKind

def sample():
    members = (CommunityMember("u1", MemberKind.PERSON, "A", True), CommunityMember("u2", MemberKind.PERSON, "B"))
    content = (CommunityContent("c1", "u1", ContentKind.POST, "How do I solve this problem?", ("python",), ("source:c1",)), CommunityContent("c2", "u2", ContentKind.COMMENT, "There is a hiring opportunity available.", (), ("source:c2",)))
    return members, content

def test_observation_analysis_and_plan_are_bounded_and_deterministic():
    members, content = sample(); engine = CommunityIntelligence(); obs = engine.observe("community-1", members, content)
    assert engine.plan(obs) == engine.plan(obs)
    assert engine.plan(obs).signals[0].kind in {SignalKind.QUESTION, SignalKind.OPPORTUNITY}
    assert engine.plan(obs).drafts

def test_unknown_author_fails_closed():
    members, _ = sample()
    try: CommunityIntelligence().observe("c", members, (CommunityContent("c1", "unknown", ContentKind.POST, "hello"),))
    except ValueError as exc: assert "author" in str(exc)
    else: raise AssertionError("unknown author must fail")

def test_policy_requires_authorized_owner_and_platform_for_publication():
    signal = CommunitySignal("c", "x", SignalKind.QUESTION, "question", 0.9, 0.9, ("source:x",)); policy = CommunityPolicy()
    assert not policy.evaluate(signal, publish=True).allowed
    assert not policy.evaluate(signal, publish=True, platform_authorized=True).allowed
    assert policy.evaluate(signal, publish=True, platform_authorized=True, owner_approved=True).allowed

def test_risk_without_evidence_is_rejected():
    assert not CommunityPolicy().evaluate(CommunitySignal("c", "x", SignalKind.RISK, "risk", 1.0, 1.0, ())).allowed

def test_store_persists_content_addressed_plan():
    members, content = sample(); adapter = CommunityRuntimeAdapter(); run = adapter.analyze("c", members, content)
    assert len(run.stored_plan_id) == 32 and adapter.store.history("c", 1); adapter.close()

def test_no_external_publish_transport_exists_in_runtime_adapter():
    assert not hasattr(CommunityRuntimeAdapter, "publish")

def test_text_and_tag_bounds():
    from devintel.modules.community.contracts import normalize_text, normalize_tags
    assert normalize_text(" a   b ") == "a b"
    try: normalize_text("x" * 4097)
    except ValueError: pass
    else: raise AssertionError("oversized text must fail")
    assert normalize_tags(("Python", "python")) == ("python",)

def test_runtime_integration_records_telemetry():
    members, content = sample(); observations = []
    class Runtime:
        def record_operation_observation_from_result(self, *args): observations.append(args)
    integration = CommunitySubsystemIntegration(Runtime()); result = integration.analyze("c", members, content)
    assert result.plan.drafts and observations and observations[0][1] == "community.intelligence"
    integration.close()
