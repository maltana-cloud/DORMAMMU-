"""Bounded evidence acquisition over the provider router.

Provider output is untrusted evidence input. This gateway only acquires and
stores bounded research documents; verification and synthesis remain explicit
separate boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ...providers.live import ProviderRouter, ResearchRequest, ResearchResult
from .contracts import ResearchDocument
from .limits import ResearchLimits
from .store import ResearchStore, InMemoryResearchStore


@dataclass(frozen=True)
class EvidenceAcquisition:
    provider_id: str
    requested: int
    accepted: int
    duplicates: int
    rejected: int
    documents: tuple[ResearchDocument, ...]
    error: str = ""


class EvidenceAcquisitionGateway:
    """Acquire a bounded set of provider results without treating them as truth."""

    def __init__(self, router: ProviderRouter, store: ResearchStore | None = None, limits: ResearchLimits | None = None) -> None:
        if not isinstance(router, ProviderRouter):
            raise TypeError("router must be a ProviderRouter")
        self.router = router
        self.store = store or InMemoryResearchStore()
        self.limits = limits or ResearchLimits()

    def acquire(self, query: str, *, max_results: int | None = None) -> EvidenceAcquisition:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        requested = self.limits.max_candidates if max_results is None else min(int(max_results), self.limits.max_candidates)
        if requested < 1:
            raise ValueError("max_results must be positive")
        result = self.router.research(ResearchRequest(query.strip(), requested))
        if not result.success:
            return EvidenceAcquisition(result.provider_id, requested, 0, 0, 0, (), result.error)
        raw = tuple(result.output) if isinstance(result.output, tuple) else ()
        accepted: list[ResearchDocument] = []
        duplicates = rejected = 0
        for item in raw[:requested]:
            if not isinstance(item, ResearchResult) or not item.url.strip() or not item.content.strip():
                rejected += 1
                continue
            try:
                document = ResearchDocument(
                    item.url,
                    item.title.strip() or item.url,
                    item.content,
                    publisher=item.source,
                    retrieved_at=datetime.now(timezone.utc),
                    metadata=dict(item.metadata),
                )
            except (TypeError, ValueError):
                rejected += 1
                continue
            if self.store.add_document(document):
                accepted.append(document)
            else:
                duplicates += 1
        return EvidenceAcquisition(result.provider_id, requested, len(accepted), duplicates, rejected, tuple(accepted))
