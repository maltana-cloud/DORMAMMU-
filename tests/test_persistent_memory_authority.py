from datetime import datetime, timedelta, timezone

from devintel.control.authority import AuthorityMode, AuthorityStore
from devintel.memory import MemoryEntry, MemoryKind, MemoryStore


def test_memory_survives_reopen_and_expires():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as directory:
        path = f"{directory}/memory.db"
        now = datetime.now(timezone.utc)
        store = MemoryStore(path)
        entry = MemoryEntry("m1", "scope-a", MemoryKind.EPISODIC, "mission", "completed", ("e1",), 0.9, now, now + timedelta(days=1))
        store.remember(entry)
        store.close()
        reopened = MemoryStore(path)
        assert reopened.recall("scope-a", now=now) == (entry,)
        assert reopened.recall("scope-a", now=now + timedelta(days=2)) == ()
        reopened.close()


def test_memory_revision_deactivates_previous_version():
    store = MemoryStore()
    now = datetime.now(timezone.utc)
    first = MemoryEntry("m1", "scope-a", MemoryKind.SEMANTIC, "provider", "reliable", (), 0.8, now)
    second = MemoryEntry("m2", "scope-a", MemoryKind.SEMANTIC, "provider", "unreliable", (), 0.95, now, revision=2)
    store.remember(first)
    store.revise("m1", second)
    assert store.recall("scope-a", query="provider") == (second,)
    assert store.get("m1").active is False
    store.close()


def test_authority_is_durable_versioned_and_revocable():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as directory:
        path = f"{directory}/authority.db"
        now = datetime.now(timezone.utc)
        store = AuthorityStore(path)
        first = store.set("owner", "public.publish", AuthorityMode.ALLOWED, now=now)
        assert store.decide("owner", "public.publish", now=now) is AuthorityMode.ALLOWED
        second = store.set("owner", "public.publish", AuthorityMode.DENIED, expected_version=first.version, now=now + timedelta(minutes=1))
        assert second.version == first.version + 1
        store.close()
        reopened = AuthorityStore(path)
        assert reopened.decide("owner", "public.publish", now=now + timedelta(minutes=2)) is AuthorityMode.DENIED
        reopened.close()


def test_expiring_authority_becomes_denied():
    store = AuthorityStore()
    now = datetime.now(timezone.utc)
    store.set("owner", "email.create", AuthorityMode.ALLOWED, expires_at=now + timedelta(hours=1), now=now)
    assert store.decide("owner", "email.create", now=now + timedelta(minutes=30)) is AuthorityMode.ALLOWED
    assert store.decide("owner", "email.create", now=now + timedelta(hours=1)) is AuthorityMode.DENIED
    store.close()
