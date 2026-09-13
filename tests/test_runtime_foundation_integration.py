from pathlib import Path

import pytest

from devintel.capabilities import CapabilityStatus, CanaryHealth, CapabilityRequirement
from devintel.runtime.app import DORMAMMURuntime


def test_runtime_uses_persistent_lifecycle_store(tmp_path: Path):
    db = tmp_path / "lifecycle.sqlite3"
    runtime = DORMAMMURuntime(lifecycle_store_path=db)
    capability = runtime.capability_registry.get("runtime.local")
    assert capability is not None
    runtime.close()

    reopened = DORMAMMURuntime(lifecycle_store_path=db)
    assert reopened.lifecycle_history() == ()
    reopened.close()


def test_runtime_canary_path_is_bounded():
    runtime = DORMAMMURuntime()
    try:
        capability = runtime.capability_registry.get("runtime.local")
        assert capability is not None
        assert capability.status is CapabilityStatus.ACTIVE

        decision = runtime.decide_capability(
            CapabilityRequirement("runtime-local", "local runtime", ("runtime",))
        )
        assert decision.action == "use_existing"
        assert decision.capability_id == "runtime.local"
    finally:
        runtime.close()


def test_runtime_recovery_requires_configuration():
    runtime = DORMAMMURuntime()
    try:
        with pytest.raises(RuntimeError, match="not configured"):
            runtime.begin_recovery("core", object())
    finally:
        runtime.close()
