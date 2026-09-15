import pytest

from devintel.capabilities import (
    CapabilityDescriptor,
    CapabilityEvidence,
    CapabilityResourceDiscoveryEngine,
    CapabilityResourceScheduler,
    CapabilityStatus,
    DiscoveryPolicy,
    ResourceDescriptor,
    ResourceKind,
)
from devintel.capabilities.contracts import CapabilityRequirement
from devintel.capabilities.registry import CapabilityRegistry, ResourceRegistry
from devintel.control.authority import AuthorityMode
from devintel.operations.worker import BoundedResourceWorker, WorkerOutcome, WorkerRequest
from devintel.runtime.app import DORMAMMURuntime


def _engine():
    capabilities = CapabilityRegistry()
    capabilities.register(CapabilityDescriptor(
        "model-a", "model-a", "1", ("inference",), "trusted", "Apache-2.0",
        status=CapabilityStatus.DISCOVERED, permissions=("approved",),
        metadata={"performance": "good", "security_status": "safe"},
        evidence=(CapabilityEvidence("catalog", "2026-09-15T00:00:00+00:00", "trusted", "https://example.com/evidence", "0123456789abcdef"),),
    ))
    resources = ResourceRegistry()
    resources.register(ResourceDescriptor("gpu-a", ResourceKind.GPU, "GPU A", capacity="1", availability="ready", permissions=("approved",)))
    return CapabilityResourceDiscoveryEngine(
        capability_registry=capabilities, resource_registry=resources,
        discovery_policy=DiscoveryPolicy(trusted_evidence_sources=("catalog",), require_provenance=True),
    )


def _plan(engine):
    class Scout:
        def discover(self, requirement):
            return (engine.capability_registry.get("model-a"),)
    engine.discovery.add_scout(Scout())
    scheduler = CapabilityResourceScheduler(engine)
    return scheduler, scheduler.plan(CapabilityRequirement("inference", "bounded inference", ("inference",)), resource_kind=ResourceKind.GPU)


def test_worker_requires_admission_and_releases_lease_after_success():
    engine = _engine(); scheduler, planned = _plan(engine)
    with pytest.raises(PermissionError):
        BoundedResourceWorker(scheduler).execute(planned, WorkerRequest("op-1", "model-a", {}), lambda _: None)
    admitted = scheduler.admit(planned)
    outcome = BoundedResourceWorker(scheduler).execute(
        admitted, WorkerRequest("op-1", "model-a", {"x": 1}),
        lambda request: WorkerOutcome(request.operation_id, request.capability_id, True, True, "ok", {"output": 42}, 0.0),
    )
    assert outcome.success and outcome.verified and outcome.data["output"] == 42
    assert engine.resource_manager.active_reservations() == ()
    engine.close()


def test_worker_releases_lease_when_worker_fails():
    engine = _engine(); scheduler, planned = _plan(engine); admitted = scheduler.admit(planned)
    def failing(_):
        raise RuntimeError("worker failure")
    with pytest.raises(RuntimeError, match="worker failure"):
        BoundedResourceWorker(scheduler).execute(admitted, WorkerRequest("op-2", "model-a", {}), failing)
    assert engine.resource_manager.active_reservations() == ()
    engine.close()


def test_worker_rejects_capability_mismatch_without_consuming_lease():
    engine = _engine(); scheduler, planned = _plan(engine); admitted = scheduler.admit(planned)
    with pytest.raises(PermissionError, match="does not match"):
        BoundedResourceWorker(scheduler).execute(admitted, WorkerRequest("op-3", "other", {}), lambda _: None)
    assert engine.resource_manager.active_reservations()
    scheduler.release(admitted)
    engine.close()


def test_runtime_worker_requires_authority_and_releases_lease_on_denial():
    engine = _engine(); scheduler, planned = _plan(engine); admitted = scheduler.admit(planned)
    runtime = DORMAMMURuntime()
    worker_called = False
    def worker(_):
        nonlocal worker_called
        worker_called = True
        return WorkerOutcome("op-4", "model-a", True, True, "ok", {}, 0.0)
    with pytest.raises(PermissionError, match="denied by runtime authority"):
        BoundedResourceWorker(scheduler, runtime).execute(admitted, WorkerRequest("op-4", "model-a", {}), worker, scope_id="test")
    assert not worker_called
    assert engine.resource_manager.active_reservations() == ()
    runtime.close(); engine.close()


def test_runtime_worker_records_verified_outcome_and_measured_duration():
    engine = _engine(); scheduler, planned = _plan(engine); admitted = scheduler.admit(planned)
    runtime = DORMAMMURuntime()
    runtime.set_authority("test", "model-a", AuthorityMode.ALLOWED)
    outcome = BoundedResourceWorker(scheduler, runtime).execute(
        admitted, WorkerRequest("op-5", "model-a", {}),
        lambda request: WorkerOutcome(request.operation_id, request.capability_id, True, True, "ok", {"output": 7}, 999.0),
        scope_id="test", verifier=lambda result: result.data.get("output") == 7,
    )
    history = runtime.operation_history("model-a")
    assert outcome.success and outcome.verified and outcome.duration_ms < 999.0
    assert len(history) == 1 and history[0].operation_id == "op-5" and history[0].verified
    assert engine.resource_manager.active_reservations() == ()
    runtime.close(); engine.close()


def test_runtime_worker_records_failed_verification_and_releases_lease():
    engine = _engine(); scheduler, planned = _plan(engine); admitted = scheduler.admit(planned)
    runtime = DORMAMMURuntime()
    runtime.set_authority("test", "model-a", AuthorityMode.ALLOWED)
    outcome = BoundedResourceWorker(scheduler, runtime).execute(
        admitted, WorkerRequest("op-6", "model-a", {}),
        lambda request: WorkerOutcome(request.operation_id, request.capability_id, True, True, "ok", {"output": 7}, 0.0),
        scope_id="test", verifier=lambda _: False,
    )
    assert outcome.success and not outcome.verified
    history = runtime.operation_history("model-a")
    assert len(history) == 1 and not history[0].verified
    assert engine.resource_manager.active_reservations() == ()
    runtime.close(); engine.close()
