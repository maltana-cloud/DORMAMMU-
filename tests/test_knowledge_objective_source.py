from devintel.intelligence import KnowledgeIntelligence
from devintel.intelligence.objective_sources import KnowledgeObjectivePolicy, KnowledgeObjectiveSource
from devintel.modules.research import Claim, VerifiedClaim
from devintel.modules.research.verification import VerificationResult
from devintel.persistence import KnowledgeStore


def verified(subject, predicate, object_value, confidence=0.9):
    return VerifiedClaim(Claim(subject, predicate, object_value), VerificationResult(True, confidence, ("source:test",)))


def test_source_derives_bounded_deterministic_candidates():
    store = KnowledgeStore()
    knowledge = KnowledgeIntelligence(store)
    knowledge.admit("scope", [verified("A", "status", "ready", .9), verified("B", "status", "ready", .8)])
    source = KnowledgeObjectiveSource(knowledge)
    first = source.candidates("scope")
    second = source.candidates("scope")
    assert first == second
    assert len(first) == 2
    assert first[0].source == "verified-knowledge"
    assert first[0].evidence_cycle_ids == (first[0].objective_id.removeprefix("knowledge:"),)


def test_source_excludes_low_confidence_and_respects_scope():
    store = KnowledgeStore()
    knowledge = KnowledgeIntelligence(store)
    knowledge.admit("scope-a", [verified("A", "status", "ready", .69)])
    knowledge.admit("scope-b", [verified("B", "status", "ready", .95)])
    source = KnowledgeObjectiveSource(knowledge, policy=KnowledgeObjectivePolicy(min_confidence=.7))
    assert source.candidates("scope-a") == ()
    assert len(source.candidates("scope-b")) == 1


def test_source_policy_bounds_results():
    store = KnowledgeStore()
    knowledge = KnowledgeIntelligence(store)
    knowledge.admit("scope", [verified(str(i), "status", "ready", .9) for i in range(5)])
    source = KnowledgeObjectiveSource(knowledge, policy=KnowledgeObjectivePolicy(max_candidates=2))
    assert len(source.candidates("scope")) == 2
