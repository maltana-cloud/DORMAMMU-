from datetime import datetime, timedelta, timezone

from devintel.intelligence.global_discovery import GlobalDiscoveryEngine, GlobalDiscoveryPolicy
from devintel.modules.growth.awareness import AwarenessObservation
from devintel.modules.growth.contracts import SignalKind

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


class Source:
    def __init__(self, source_id, observations=(), healthy=True, error=False):
        self.source_id = source_id
        self.observations = tuple(observations)
        self._healthy = healthy
        self.error = error
        self.calls = 0

    def health(self):
        return self._healthy

    def discover(self, *, scope_id, query, limit):
        self.calls += 1
        if self.error:
            raise RuntimeError("source failure")
        return self.observations[:limit]


def obs(source, summary, importance=.5, confidence=.8, at=NOW):
    return AwarenessObservation(source, "global", summary, SignalKind.AUDIENCE_NEED, (), at, confidence, importance)


def test_round_is_bounded_deterministic_and_deduplicated():
    a = Source("a", [obs("a", "same", .5), obs("a", "low", .2)])
    b = Source("b", [obs("b", "same", .9), obs("b", "other", .8)])
    engine = GlobalDiscoveryEngine([b, a], policy=GlobalDiscoveryPolicy(max_observations=2))
    result = engine.run_round(scope_id="global", query="needs", now=NOW)
    assert [item.summary for item in result.observations] == ["same", "other"]
    assert result.next_run_at == NOW + timedelta(seconds=300)
    assert result.observations[0].source_id == "b"


def test_unhealthy_and_failing_sources_are_isolated():
    bad = Source("bad", healthy=False)
    failing = Source("fail", error=True)
    good = Source("good", [obs("good", "usable")])
    result = GlobalDiscoveryEngine([bad, failing, good]).run_round(scope_id="global", query="q", now=NOW)
    assert [item.summary for item in result.observations] == ["usable"]
    assert result.rejected == 2
    assert bad.calls == 0


def test_stale_future_and_wrong_scope_observations_are_rejected():
    stale = obs("s", "stale", at=NOW - timedelta(days=2))
    future = obs("s", "future", at=NOW + timedelta(minutes=1))
    wrong = AwarenessObservation("s", "other", "wrong", SignalKind.AUDIENCE_NEED, (), NOW, .9, .9)
    source = Source("s", [stale, future, wrong])
    engine = GlobalDiscoveryEngine([source], policy=GlobalDiscoveryPolicy(max_age_seconds=3600))
    result = engine.run_round(scope_id="global", query="q", now=NOW)
    assert result.observations == ()
    assert result.rejected == 3


def test_due_is_external_scheduler_boundary():
    engine = GlobalDiscoveryEngine([])
    assert engine.due(NOW, None)
    assert not engine.due(NOW, NOW + timedelta(seconds=1))
    assert engine.due(NOW + timedelta(seconds=1), NOW + timedelta(seconds=1))
