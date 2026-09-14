from devintel.autonomy import AutonomousCycle, AutonomousCycleStore, AutonomyPhase


def test_autonomous_cycle_store_persists_and_reopens(tmp_path):
    path = str(tmp_path / "cycles.sqlite")
    store = AutonomousCycleStore(path)
    cycle = AutonomousCycle("cycle-1", "scope", tuple(AutonomyPhase), 1, 1, 0, True, False, "", 1)
    store.record(cycle)
    store.close()

    reopened = AutonomousCycleStore(path)
    history = reopened.history("scope")
    reopened.close()
    assert history == (cycle,)
