from datetime import datetime, timedelta, timezone

import pytest

from devintel.modules.growth.awareness import AwarenessAggregator, AwarenessObservation
from devintel.modules.growth.contracts import SignalKind


NOW = datetime(2026, 9, 14, 12, tzinfo=timezone.utc)


def observation(summary, *, source="source-a", age_hours=1, importance=0.8, confidence=0.9, scope="scope-a"):
    return AwarenessObservation(
        source,
        scope,
        summary,
        SignalKind.AUDIENCE_NEED,
        ("https://example.com/evidence",),
        NOW - timedelta(hours=age_hours),
        confidence,
        importance,
    )


def test_aggregation_filters_scope_deduplicates_and_ranks():
    items = [
        observation("same need", age_hours=48, importance=0.7),
        observation("same need", age_hours=1, importance=0.7),
        observation("urgent need", age_hours=2, importance=1.0, source="source-b"),
        observation("other scope", scope="scope-b"),
    ]
    signals = AwarenessAggregator().aggregate(items, scope_id="scope-a", now=NOW)
    assert len(signals) == 2
    assert signals[0].summary == "urgent need"
    assert signals[0].metadata["importance"] == 1.0
    assert signals[1].summary == "same need"


def test_aggregation_is_bounded():
    items = [observation(f"need-{i}", source=f"source-{i}") for i in range(100)]
    signals = AwarenessAggregator(max_signals=5).aggregate(items, scope_id="scope-a", now=NOW)
    assert len(signals) == 5


def test_rejects_untrusted_evidence_urls():
    with pytest.raises(ValueError):
        AwarenessObservation(
            "source-a", "scope-a", "need", evidence_urls=("http://example.com",)
        )
