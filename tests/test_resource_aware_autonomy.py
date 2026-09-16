from devintel.autonomy import Observation
from devintel.capabilities import ResourceDescriptor, ResourceKind, ResourceRequest
from devintel.core.contracts import ActionRequest
from devintel.runtime.app import DEVINTELRuntime


def test_resource_aware_engine_reserves_only_during_act_and_releases():
    runtime = DEVINTELRuntime()
    runtime.register_resource(ResourceDescriptor(
        "test:cpu", ResourceKind.CPU, "test cpu", capacity="2", availability="ready",
        permissions=("approved",), metadata={"allocatable": "2"},
    ))
    runtime.register_action("ping", lambda payload: {"ok": True})
    engine = runtime.resource_aware_autonomous_engine(
        lambda scope: [Observation(scope, "signal")],
        lambda scope, observations: [ActionRequest("ping", payload={
            "_scope_id": scope,
            "_resource_request": ResourceRequest(ResourceKind.CPU, 1),
        })],
        lambda scope, results: len(results) == 1 and results[0].success,
    )
    assert runtime.resource_reservations() == ()
    cycle = engine.run_once("scope")
    assert cycle.verified is True
    assert runtime.resource_reservations() == ()
    runtime.close()


def test_resource_aware_engine_fails_closed_without_capacity():
    runtime = DEVINTELRuntime()
    runtime.register_action("ping", lambda payload: {"ok": True})
    engine = runtime.resource_aware_autonomous_engine(
        lambda scope: [Observation(scope, "signal")],
        lambda scope, observations: [ActionRequest("ping", payload={
            "_scope_id": scope,
            "_resource_request": ResourceRequest(ResourceKind.GPU, 1),
        })],
        lambda scope, results: bool(results) and not results[0].success,
    )
    cycle = engine.run_once("scope")
    assert cycle.verified is True
    assert runtime.snapshot("scope").metrics["requests.succeeded"] == 0
    assert runtime.resource_reservations() == ()
    runtime.close()


def test_resource_aware_engine_never_leaks_lease_when_action_fails():
    runtime = DEVINTELRuntime()
    runtime.register_resource(ResourceDescriptor(
        "test:cpu", ResourceKind.CPU, "test cpu", capacity="1", availability="ready",
        permissions=("approved",), metadata={"allocatable": "1"},
    ))
    runtime.register_action("fail", lambda payload: None)
    engine = runtime.resource_aware_autonomous_engine(
        lambda scope: [Observation(scope, "signal")],
        lambda scope, observations: [ActionRequest("fail", payload={
            "_scope_id": scope,
            "_resource_request": ResourceRequest(ResourceKind.CPU, 1),
        })],
        lambda scope, results: bool(results) and not results[0].success,
    )
    cycle = engine.run_once("scope")
    assert cycle.verified is True
    assert runtime.resource_reservations() == ()
    runtime.close()
