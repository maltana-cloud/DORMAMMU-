import pytest

from devintel.capabilities import ResourceLeaseStore


def test_lease_survives_store_reopen(tmp_path):
    path = str(tmp_path / "leases.sqlite3")
    first = ResourceLeaseStore(path)
    lease = first.acquire("cpu", 2, 4, ttl_seconds=60, now=100)
    assert lease is not None
    first.close()

    second = ResourceLeaseStore(path)
    try:
        assert second.get(lease.lease_id, now=101) == lease
        assert second.active_quantity("cpu", now=101) == 2
    finally:
        second.close()


def test_lease_capacity_is_atomic_and_expiry_frees_capacity(tmp_path):
    store = ResourceLeaseStore(str(tmp_path / "leases.sqlite3"))
    try:
        first = store.acquire("gpu", 3, 4, ttl_seconds=10, now=100)
        assert first is not None
        assert store.acquire("gpu", 2, 4, ttl_seconds=10, now=101) is None
        expired = store.acquire("gpu", 2, 4, ttl_seconds=10, now=111)
        assert expired is not None
        assert store.active_quantity("gpu", now=111) == 2
    finally:
        store.close()


def test_release_is_idempotency_protected(tmp_path):
    store = ResourceLeaseStore(str(tmp_path / "leases.sqlite3"))
    try:
        lease = store.acquire("ram", 1, 2, ttl_seconds=60, now=100)
        assert lease is not None
        store.release(lease.lease_id)
        with pytest.raises(KeyError):
            store.release(lease.lease_id)
    finally:
        store.close()


def test_invalid_lease_request_is_rejected(tmp_path):
    store = ResourceLeaseStore(str(tmp_path / "leases.sqlite3"))
    try:
        with pytest.raises(ValueError):
            store.acquire("cpu", 0, 4)
        with pytest.raises(ValueError):
            store.acquire("cpu", 1, 4, ttl_seconds=0)
    finally:
        store.close()
