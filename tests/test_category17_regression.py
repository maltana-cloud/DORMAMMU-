from devintel.runtime import DORMAMMURuntime, RuntimeJobStore, RuntimeWorker


def test_public_runtime_imports_remain_compatible():
    assert DORMAMMURuntime() is not None


def test_runtime_worker_factory_and_execution_remain_bounded():
    store = RuntimeJobStore()
    store.enqueue("scope", "noop", {})
    seen = []
    worker = __import__("devintel.runtime", fromlist=["build_worker"]).build_worker(store, lambda job: seen.append(job.action))
    result = worker.run_once(max_jobs=1)
    assert len(result) == 1
    assert result[0].status == "succeeded"
    assert seen == ["noop"]
    store.close()
