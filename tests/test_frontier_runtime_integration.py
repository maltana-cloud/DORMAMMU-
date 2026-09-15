from devintel.frontier import FrontierReflection, JobState
from devintel.runtime import DORMAMMURuntime


def test_runtime_composes_frontier_control_plane_and_persists_jobs(tmp_path):
    path = tmp_path / "frontier.db"
    runtime = DORMAMMURuntime(frontier_store_path=str(path))
    job = runtime.frontier_submit(scope_id="research", kind="research", payload={"query": "test"}, max_attempts=2)
    claimed = runtime.frontier.store.claim(worker_id="worker-a", now=10, lease_ttl=30)
    assert claimed is not None
    assert claimed.job_id == job.job_id
    completed = runtime.frontier.store.complete(job.job_id, worker_id="worker-a", now=11, success=True)
    assert completed.state is JobState.SUCCEEDED
    reflection_id = runtime.frontier_reflect(
        FrontierReflection(job.job_id, "succeeded", ("evidence:1",), "successful bounded execution")
    )
    assert reflection_id
    runtime.close()

    reopened = DORMAMMURuntime(frontier_store_path=str(path))
    assert reopened.frontier.store.get(job.job_id).state is JobState.SUCCEEDED
    assert reopened.frontier.store.reflections(job.job_id)[0].lesson == "successful bounded execution"
    reopened.close()
