from devintel.persistence import KnowledgeRecord, KnowledgeStore


def test_knowledge_and_state_survive_reopen(tmp_path):
    path = tmp_path / "intelligence.db"
    first = KnowledgeStore(path)
    saved = first.save_knowledge(KnowledgeRecord("k1", "scope-a", "fact", "verified claim", ("source:1",)))
    state = first.put_state("scope-a", "research", {"phase": "discovery", "count": 2})
    assert saved.version == 1
    assert state.version == 1
    first.close()

    second = KnowledgeStore(path)
    assert second.get_knowledge("k1", scope_id="scope-a").content == "verified claim"
    assert second.get_state("scope-a", "research").value == {"phase": "discovery", "count": 2}
    assert second.snapshot().schema_version == 1
    second.close()


def test_scope_isolation_and_versioning(tmp_path):
    store = KnowledgeStore(tmp_path / "intelligence.db")
    store.save_knowledge(KnowledgeRecord("k1", "a", "fact", "one"))
    updated = store.save_knowledge(KnowledgeRecord("k1", "a", "fact", "two"))
    store.save_knowledge(KnowledgeRecord("k2", "b", "fact", "other"))
    assert updated.version == 2
    assert store.get_knowledge("k1", scope_id="b") is None
    assert [r.record_id for r in store.list_knowledge("a")] == ["k1"]
    store.close()


def test_state_versions_advance_and_missing_state_is_none(tmp_path):
    store = KnowledgeStore(tmp_path / "intelligence.db")
    assert store.get_state("a", "missing") is None
    assert store.put_state("a", "x", {"v": 1}).version == 1
    assert store.put_state("a", "x", {"v": 2}).version == 2
    assert store.get_state("a", "x").value == {"v": 2}
    store.close()
