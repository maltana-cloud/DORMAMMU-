from devintel.autonomy import Observation
from devintel.core.contracts import ActionRequest
from devintel.runtime.app import DEVINTELRuntime


def test_runtime_exposes_autonomous_engine_through_core():
    runtime = DEVINTELRuntime()
    runtime.register_action("ping", lambda payload: {"ok": True})
    engine = runtime.autonomous_engine(
        lambda scope: [Observation(scope, "signal")],
        lambda scope, observations: [ActionRequest("ping", payload={"_scope_id": scope})],
        lambda scope, results: results[0].success,
    )
    cycle = engine.run_once("scope")
    assert cycle.verified is True
    assert runtime.snapshot("scope").metrics["requests.succeeded"] == 1
    assert runtime.autonomous_cycle_history("scope") == (cycle,)
    runtime.close()


def test_runtime_autonomy_store_survives_reopen(tmp_path):
    path = str(tmp_path / "autonomy.sqlite")
    runtime = DEVINTELRuntime(autonomy_store_path=path)
    runtime.register_action("ping", lambda payload: {"ok": True})
    engine = runtime.autonomous_engine(
        lambda scope: [Observation(scope, "signal")],
        lambda scope, observations: [ActionRequest("ping", payload={"_scope_id": scope})],
        lambda scope, results: results[0].success,
    )
    cycle = engine.run_once("scope")
    runtime.close()
    reopened = DEVINTELRuntime(autonomy_store_path=path)
    assert reopened.autonomous_cycle_history("scope") == (cycle,)
    reopened.close()
