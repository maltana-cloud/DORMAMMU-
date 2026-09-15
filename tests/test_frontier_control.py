from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from devintel.frontier import (
    CredentialReference,
    FrontierControlPlane,
    FrontierJobStore,
    FrontierReflection,
    FrontierResourceBudget,
    JobState,
)


def test_credential_reference_never_contains_secret_and_validates_scope() -> None:
    reference = CredentialReference("provider-a", "secret-manager:key-1", "publish")
    assert reference.provider_id == "provider-a"
    assert reference.reference_id == "secret-manager:key-1"
    assert reference.scope == "publish"
    with pytest.raises(ValueError):
        CredentialReference("provider-a", "", "publish")
    with pytest.raises(ValueError):
        CredentialReference("provider-a", "key\nvalue", "publish")


def test_atomic_claim_allows_one_worker_and_expiry_takeover() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory) / "frontier.db")
        first = FrontierJobStore(path)
        second = FrontierJobStore(path)
        first.enqueue(scope_id="s", kind="research", payload={"q": "x"}, job_id="job-1")

        claimed_a = first.claim(worker_id="worker-a", now=10, lease_ttl=5)
        claimed_b = second.claim(worker_id="worker-b", now=10, lease_ttl=5)
        assert claimed_a is not None
        assert claimed_b is None
        assert claimed_a.worker_id == "worker-a"

        assert second.recover_expired(now=16) == 1
        takeover = second.claim(worker_id="worker-b", now=16, lease_ttl=5)
        assert takeover is not None
        assert takeover.worker_id == "worker-b"
        first.close()
        second.close()


def test_expired_worker_cannot_complete_before_or_after_takeover() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory) / "frontier.db")
        first = FrontierJobStore(path)
        second = FrontierJobStore(path)
        first.enqueue(scope_id="s", kind="task", payload={}, job_id="job-1")
        assert first.claim(worker_id="a", now=1, lease_ttl=2)
        with pytest.raises(ValueError):
            first.complete("job-1", worker_id="a", now=4, success=True)
        assert second.recover_expired(now=4) == 1
        assert second.claim(worker_id="b", now=4, lease_ttl=2) is not None
        with pytest.raises(ValueError):
            first.complete("job-1", worker_id="a", now=4, success=True)
        done = second.complete("job-1", worker_id="b", now=5, success=True)
        assert done.state is JobState.SUCCEEDED
        first.close()
        second.close()


def test_retry_then_dead_letter_is_bounded() -> None:
    store = FrontierJobStore()
    store.enqueue(scope_id="s", kind="task", payload={}, max_attempts=2, job_id="job-1")
    assert store.claim(worker_id="a", now=1, lease_ttl=10)
    retry = store.complete("job-1", worker_id="a", now=2, success=False, error="first", retry_delay=3)
    assert retry.state is JobState.QUEUED
    assert retry.attempts == 1
    assert store.claim(worker_id="a", now=5, lease_ttl=10)
    dead = store.complete("job-1", worker_id="a", now=6, success=False, error="second")
    assert dead.state is JobState.DEAD_LETTER
    assert dead.attempts == 2
    store.close()


def test_resource_budget_is_atomic_and_scope_bound() -> None:
    store = FrontierJobStore()
    store.register_budget(FrontierResourceBudget("cpu", "s", 3.0))
    assert store.reserve(resource_id="cpu", quantity=2.0, scope_id="s")
    assert not store.reserve(resource_id="cpu", quantity=2.0, scope_id="s")
    assert not store.reserve(resource_id="cpu", quantity=1.0, scope_id="other")
    assert store.release(resource_id="cpu", quantity=1.0, scope_id="s")
    assert store.reserve(resource_id="cpu", quantity=2.0, scope_id="s")
    store.close()


def test_reflection_is_deterministic_and_bounded() -> None:
    store = FrontierJobStore()
    reflection = FrontierReflection("job-1", "success", ("evidence-1",), "provider fallback worked")
    first = store.record_reflection(reflection, recorded_at=10)
    second = store.record_reflection(reflection, recorded_at=20)
    assert first == second
    assert store.reflections("job-1") == (reflection,)
    store.close()


def test_control_plane_submits_and_reflects() -> None:
    control = FrontierControlPlane()
    job = control.submit(scope_id="s", kind="research", payload={"topic": "x"}, priority=4)
    assert job.state is JobState.QUEUED
    assert control.reflect(FrontierReflection(job.job_id, "queued", (), "awaiting worker"))
    control.close()
