from devintel.capabilities import CapabilityLifecycle, CapabilityRegistry, CapabilityStatus, CapabilityDescriptor, LifecycleStore


def descriptor(status=CapabilityStatus.DISCOVERED):
    return CapabilityDescriptor("research", "Research", "1.0", ("research",), "trusted", "MIT", status=status)


def test_lifecycle_store_persists_events(tmp_path):
    path = tmp_path / "lifecycle.db"
    store = LifecycleStore(path)
    registry = CapabilityRegistry()
    registry.register(descriptor(CapabilityStatus.REGISTERED))
    lifecycle = CapabilityLifecycle(registry, recorder=store.record)
    lifecycle.canary("research")
    lifecycle.activate("research")
    store.close()

    reopened = LifecycleStore(path)
    history = reopened.history("research")
    assert [event.to_status for event in history] == [CapabilityStatus.CANARY, CapabilityStatus.ACTIVE]
    reopened.close()


def test_runtime_default_store_is_memory_only():
    from devintel.runtime import DORMAMMURuntime
    runtime = DORMAMMURuntime()
    assert runtime.lifecycle_history() == ()
    runtime.close()
