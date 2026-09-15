"""Bounded human-collaboration contracts for DORMAMMU.

Human input is treated as data until it passes explicit validation. This
module creates reviewable requests and responses; it does not grant authority
or execute consequential actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Iterable

from ..modules.research.normalization import normalize_text


class CollaborationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class CollaborationRequest:
    request_id: str
    scope_id: str
    objective: str
    context: str = ""
    evidence: tuple[str, ...] = ()
    status: CollaborationStatus = CollaborationStatus.PENDING

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id is required")
        if not isinstance(self.scope_id, str) or not self.scope_id.strip():
            raise ValueError("scope_id is required")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective is required")
        if not isinstance(self.context, str):
            raise TypeError("context must be a string")
        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be a tuple")
        evidence = tuple(url.strip() for url in self.evidence if isinstance(url, str) and url.strip())
        object.__setattr__(self, "evidence", evidence)
        if not isinstance(self.status, CollaborationStatus):
            raise TypeError("status must be CollaborationStatus")


@dataclass(frozen=True)
class CollaborationResponse:
    request_id: str
    responder_id: str
    message: str
    accepted: bool
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id is required")
        if not isinstance(self.responder_id, str) or not self.responder_id.strip():
            raise ValueError("responder_id is required")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message is required")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be boolean")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")


class HumanCollaborationEngine:
    """Create deterministic, reviewable collaboration requests/responses."""

    def __init__(self, *, max_context: int = 20_000, max_evidence: int = 20) -> None:
        if max_context <= 0 or max_evidence <= 0:
            raise ValueError("collaboration bounds must be positive")
        self.max_context = max_context
        self.max_evidence = max_evidence

    @staticmethod
    def _normalize_evidence(evidence: Iterable[str]) -> tuple[str, ...]:
        if isinstance(evidence, (str, bytes)):
            raise TypeError("evidence must be an iterable of strings, not a string")
        try:
            values = tuple(evidence)
        except TypeError as exc:
            raise TypeError("evidence must be iterable") from exc
        if any(not isinstance(url, str) for url in values):
            raise TypeError("evidence entries must be strings")
        normalized = tuple(url.strip() for url in values if url.strip())
        return normalized

    def create_request(
        self,
        scope_id: str,
        objective: str,
        *,
        context: str = "",
        evidence: Iterable[str] = (),
    ) -> CollaborationRequest:
        normalized_scope = normalize_text(scope_id)
        normalized_objective = normalize_text(objective)
        if not normalized_scope or not normalized_objective:
            raise ValueError("scope_id and objective are required")
        if not isinstance(context, str):
            raise TypeError("context must be a string")
        normalized_context = context.strip()
        if len(normalized_context) > self.max_context:
            raise ValueError("context exceeds configured bound")
        normalized_evidence = self._normalize_evidence(evidence)
        if len(normalized_evidence) > self.max_evidence:
            raise ValueError("evidence exceeds configured bound")
        payload = "\x1f".join(
            (normalized_scope, normalized_objective, normalized_context, *normalized_evidence)
        )
        request_id = "collab-" + sha256(payload.encode("utf-8")).hexdigest()
        return CollaborationRequest(
            request_id,
            normalized_scope,
            normalized_objective,
            normalized_context,
            normalized_evidence,
        )

    @staticmethod
    def respond(
        request: CollaborationRequest,
        responder_id: str,
        message: str,
        *,
        accepted: bool,
        reason: str = "",
    ) -> CollaborationResponse:
        if not isinstance(request, CollaborationRequest):
            raise TypeError("request must be CollaborationRequest")
        return CollaborationResponse(request.request_id, responder_id, message, accepted, reason)

    @staticmethod
    def apply_response(
        request: CollaborationRequest,
        response: CollaborationResponse,
    ) -> CollaborationRequest:
        if not isinstance(request, CollaborationRequest):
            raise TypeError("request must be CollaborationRequest")
        if not isinstance(response, CollaborationResponse):
            raise TypeError("response must be CollaborationResponse")
        if response.request_id != request.request_id:
            raise ValueError("response does not match request")
        if request.status is not CollaborationStatus.PENDING:
            raise ValueError("only pending requests can receive a response")
        status = CollaborationStatus.ACCEPTED if response.accepted else CollaborationStatus.REJECTED
        return CollaborationRequest(
            request.request_id,
            request.scope_id,
            request.objective,
            request.context,
            request.evidence,
            status,
        )
