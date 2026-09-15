from devintel.runtime import RuntimeJobStore, RuntimeScheduler, RuntimeWorker, ScheduledJob


def test_jobs_survive_store_reopen(tmp_path):
    path = tmp_path / "jobs.db"
    first = RuntimeJobStore(str(path))
    job = first.enqueue("scope", "action", {"value": 1})
    first.close()

    second = RuntimeJobStore(str(path))
    assert second.get(job.job_id).status == "queued"
    claimed = second.claim_next()
    assert claimed.job_id == job.job_id
    second.complete(job.job_id)
    assert second.get(job.job_id).status == "succeeded"
    second.close()


def test_running_jobs_are_recovered_after_restart(tmp_path):
    path = tmp_path / "jobs.db"
    first = RuntimeJobStore(str(path))
    job = first.enqueue("scope", "action", {})
    first.claim_next()
    first.close()

    second = RuntimeJobStore(str(path))
    recovered = second.recover_running()
    assert recovered[0].job_id == job.job_id
    assert second.get(job.job_id).status == "queued"
    second.close()


def test_worker_is_bounded_and_records_failure(tmp_path):
    store = RuntimeJobStore(str(tmp_path / "jobs.db"))
    store.enqueue("scope", "ok", {})
    store.enqueue("scope", "bad", {})
    calls = []

    def dispatch(job):
        calls.append(job.action)
        if job.action == "bad":
            raise RuntimeError("boom")

    worker = RuntimeWorker(store, dispatch)
    first = worker.run_once(max_jobs=1)
    assert len(first) == 1
    assert calls == ["ok"]
    second = worker.run_once(max_jobs=1)
    assert second[0].status == "failed"
    assert store.get(second[0].job_id).last_error == "RuntimeError"
    store.close()


def test_scheduler_enqueues_due_work_without_background_loop(tmp_path):
    store = RuntimeJobStore(str(tmp_path / "jobs.db"))
    scheduler = RuntimeScheduler(store)
    scheduler.register(ScheduledJob("s", "scope", "action", {"x": 1}, 60, 100))

    assert scheduler.tick(now=99, max_jobs=1) == ()
    jobs = scheduler.tick(now=100, max_jobs=1)
    assert len(jobs) == 1
    assert jobs[0].scope_id == "scope"
    assert scheduler.tick(now=100, max_jobs=1) == ()
    store.close()


def test_scheduler_validates_limits_and_can_disable(tmp_path):
    store = RuntimeJobStore(str(tmp_path / "jobs.db"))
    scheduler = RuntimeScheduler(store)
    scheduler.register(ScheduledJob("s", "scope", "action", {}, 10, 1))
    scheduler.disable("s")
    assert scheduler.tick(now=100) == ()
    store.close()
