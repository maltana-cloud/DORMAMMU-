from datetime import datetime, timedelta, timezone

from devintel.control import AuthorityMode
from devintel.memory import MemoryEntry, MemoryKind
from devintel.runtime import DORMAMMURuntime


def test_runtime_composes_persistent_memory_and_revocable_authority():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as directory:
        memory_path = f"{directory}/memory.db"
        authority_path = f"{directory}/authority.db"
        now = datetime.now(timezone.utc)
        first = DORMAMMURuntime(memory_store_path=memory_path, authority_store_path=authority_path)
        entry = MemoryEntry("m1", "scope-a", MemoryKind.MISSION, "mission-1", "completed", ("frontier:1",), 0.9, now)
        first.remember(entry)
        first.set_authority("owner", "public.publish", AuthorityMode.ALLOWED, now=now)
        assert first.authority("owner", "public.publish") is AuthorityMode.ALLOWED
        first.close()

        second = DORMAMMURuntime(memory_store_path=memory_path, authority_store_path=authority_path)
        assert second.recall_memory("scope-a")[0] == entry
        second.set_authority("owner", "public.publish", AuthorityMode.DENIED, now=now + timedelta(minutes=1), expected_version=1)
        assert second.authority("owner", "public.publish") is AuthorityMode.DENIED
        second.close()


def test_runtime_authority_defaults_to_deny_and_supports_expiry():
    runtime = DORMAMMURuntime()
    now = datetime.now(timezone.utc)
    try:
        assert runtime.authority("owner", "email.create") is AuthorityMode.DENIED
        runtime.set_authority("owner", "email.create", AuthorityMode.ALLOWED, expires_at=now + timedelta(minutes=1), now=now)
        assert runtime.authority("owner", "email.create") is AuthorityMode.ALLOWED
        assert runtime.authority_store.decide("owner", "email.create", now=now + timedelta(minutes=2)) is AuthorityMode.DENIED
    finally:
        runtime.close()
