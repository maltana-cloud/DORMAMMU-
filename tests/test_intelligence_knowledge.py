from pathlib import Path

from devintel.intelligence import KnowledgeIntelligence, KnowledgeQuery
from devintel.modules.research import Claim, VerifiedClaim
from devintel.modules.research.verification import VerificationResult
from devintel.persistence import KnowledgeStore


def verified(subject, predicate, object_value, *, confidence=0.9, url="https://example.com/source"):
    claim = Claim(subject, predicate, object_value, confidence, (url,))
    verification = VerificationResult(True, confidence, (), (url,))
    return VerifiedClaim(claim, verification)


def test_only_verified_claims_are_admitted_and_provenance_is_preserved():
    store = KnowledgeStore()
    intelligence = KnowledgeIntelligence(store)
    item = intelligence.admit("scope-a", [verified("DORMAMMU", "motto", "Beyond What Is Known")])[0]
    assert item.provenance == ("https://example.com/source",)
    assert item.confidence == 0.9
    assert intelligence.query(KnowledgeQuery("scope-a", "motto"))[0].object == "Beyond What Is Known"
    store.close()


def test_unverified_claim_cannot_cross_the_admission_boundary():
    store = KnowledgeStore()
    intelligence = KnowledgeIntelligence(store)
    claim = Claim("x", "status", "unknown", 1.0, ("https://example.com/source",))
    try:
        intelligence.admit("scope", [claim])
    except TypeError:
        pass
    else:
        raise AssertionError("unverified claim was admitted")
    assert intelligence.query(KnowledgeQuery("scope")).__len__() == 0
    store.close()


def test_scope_isolation_and_deterministic_bounded_retrieval():
    store = KnowledgeStore()
    intelligence = KnowledgeIntelligence(store, max_results=2)
    intelligence.admit("a", [verified("x", "type", "one", confidence=0.7), verified("y", "type", "two", confidence=0.9), verified("z", "type", "three", confidence=0.8)])
    intelligence.admit("b", [verified("x", "type", "other", confidence=1.0)])
    result = intelligence.query(KnowledgeQuery("a", "type", limit=2))
    assert [item.object for item in result] == ["two", "three"]
    assert all(item.scope_id == "a" for item in result)
    store.close()


def test_conflicts_are_explicit_not_silently_resolved():
    store = KnowledgeStore()
    intelligence = KnowledgeIntelligence(store)
    intelligence.admit("scope", [verified("x", "status", "active", confidence=0.9), verified("x", "status", "inactive", confidence=0.8)])
    conflicts = intelligence.conflicts("scope")
    assert len(conflicts) == 1
    assert conflicts[0].objects == ("active", "inactive")
    store.close()


def test_duplicate_assertion_is_versioned_and_merges_provenance():
    store = KnowledgeStore()
    intelligence = KnowledgeIntelligence(store)
    first = intelligence.admit("scope", [verified("x", "status", "active", confidence=0.7, url="https://example.com/a")])[0]
    second = intelligence.admit("scope", [verified("x", "status", "active", confidence=0.9, url="https://example.com/b")])[0]
    assert second.version == first.version + 1
    item = intelligence.query(KnowledgeQuery("scope"))[0]
    assert item.confidence == 0.9
    assert item.provenance == ("https://example.com/a", "https://example.com/b")
    store.close()


def test_knowledge_survives_store_reopen(tmp_path: Path):
    path = tmp_path / "knowledge.db"
    store = KnowledgeStore(path)
    KnowledgeIntelligence(store).admit("scope", [verified("x", "status", "persistent")])
    store.close()
    reopened = KnowledgeStore(path)
    result = KnowledgeIntelligence(reopened).query(KnowledgeQuery("scope"))
    assert len(result) == 1
    assert result[0].object == "persistent"
    reopened.close()
