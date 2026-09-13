from devintel.capabilities import CanaryHealth
from devintel.operations.telemetry import OperationObservation, OperationalTelemetryStore


def observation(operation_id, success=True, verified=True, duration=10.0):
    return OperationObservation(operation_id, "capability.test", "record", success, verified, duration, "ok")


def test_telemetry_persists_and_derives_health():
    store = OperationalTelemetryStore(":memory:")
    try:
        for index in range(5):
            store.record(observation(f"op-{index}"))
        health = store.health("capability.test", window=5, min_samples=5)
        assert isinstance(health, CanaryHealth)
        assert health.success_rate == 1.0
        assert health.error_rate == 0.0
        assert health.latency_ms == 10.0
    finally:
        store.close()


def test_telemetry_fails_closed_until_minimum_sample_count():
    store = OperationalTelemetryStore(":memory:")
    try:
        for index in range(4):
            store.record(observation(f"op-{index}"))
        assert store.health("capability.test", window=5, min_samples=5) is None
    finally:
        store.close()


def test_failed_or_unverified_operations_reduce_health():
    store = OperationalTelemetryStore(":memory:")
    try:
        for index in range(4):
            store.record(observation(f"good-{index}"))
        store.record(observation("bad", success=False, verified=False, duration=6000.0))
        health = store.health("capability.test", window=5, min_samples=5)
        assert health is not None
        assert health.success_rate == 0.8
        assert abs(health.error_rate - 0.2) < 1e-12
        assert health.latency_ms == 6000.0
        assert not health.healthy
    finally:
        store.close()


def test_history_survives_close_and_reopen():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory) / "telemetry.sqlite")
        first = OperationalTelemetryStore(path)
        first.record(observation("persisted"))
        first.close()
        second = OperationalTelemetryStore(path)
        try:
            history = second.history("capability.test")
            assert len(history) == 1
            assert history[0].operation_id == "persisted"
        finally:
            second.close()
