"""Versioned registry for assessed research domains."""

from __future__ import annotations

from dataclasses import dataclass

from .domain_expansion import DomainAssessment, DomainProposal


@dataclass(frozen=True)
class DomainRecord:
    proposal: DomainProposal
    assessment: DomainAssessment
    version: int = 1


class DomainRegistry:
    """In-memory registry with explicit replacement and admission boundaries."""

    def __init__(self) -> None:
        self._records: dict[str, DomainRecord] = {}

    def register(self, proposal: DomainProposal, assessment: DomainAssessment) -> DomainRecord:
        if proposal.proposal_id != assessment.proposal_id:
            raise ValueError("assessment does not match proposal")
        if not assessment.eligible:
            raise ValueError("domain proposal is not eligible")
        previous = self._records.get(proposal.proposal_id)
        version = previous.version + 1 if previous else 1
        record = DomainRecord(proposal, assessment, version)
        self._records[proposal.proposal_id] = record
        return record

    def get(self, proposal_id: str) -> DomainRecord | None:
        return self._records.get(proposal_id)

    def list(self) -> tuple[DomainRecord, ...]:
        return tuple(self._records.values())

    def remove(self, proposal_id: str) -> bool:
        return self._records.pop(proposal_id, None) is not None
