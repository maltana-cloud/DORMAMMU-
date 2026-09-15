"""Stable, bounded contracts for social and community intelligence."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from typing import Mapping

MAX_MEMBERS = 100_000
MAX_CONTENT_ITEMS = 10_000
MAX_TEXT = 4_096
MAX_TAGS = 32
MAX_EVIDENCE = 16

class MemberKind(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    SYSTEM = "system"

class ContentKind(str, Enum):
    POST = "post"
    COMMENT = "comment"
    ANNOUNCEMENT = "announcement"

class SignalKind(str, Enum):
    QUESTION = "question"
    NEED = "need"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    DISCUSSION = "discussion"

@dataclass(frozen=True)
class CommunityMember:
    member_id: str
    kind: MemberKind
    display_name: str
    verified_identity: bool = False

@dataclass(frozen=True)
class CommunityContent:
    content_id: str
    author_id: str
    kind: ContentKind
    text: str
    tags: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()

@dataclass(frozen=True)
class CommunitySignal:
    community_id: str
    content_id: str
    kind: SignalKind
    summary: str
    relevance: float
    confidence: float
    evidence: tuple[str, ...] = ()

@dataclass(frozen=True)
class ResponseDraft:
    draft_id: str
    content_id: str
    text: str
    purpose: str
    evidence: tuple[str, ...] = ()

@dataclass(frozen=True)
class CommunityPlan:
    community_id: str
    signals: tuple[CommunitySignal, ...]
    drafts: tuple[ResponseDraft, ...]
    next_steps: tuple[str, ...]

@dataclass(frozen=True)
class CommunityPolicyDecision:
    allowed: bool
    reason: str
    requires_owner_approval: bool
    risk: str

def normalize_text(value: object) -> str:
    text = " ".join(str(value).split())
    if not text or len(text) > MAX_TEXT:
        raise ValueError("text is empty or out of bounds")
    return text

def normalize_tags(values: tuple[str, ...] | list[str] | Mapping[str, object] = ()) -> tuple[str, ...]:
    raw = values.keys() if isinstance(values, Mapping) else values
    tags = tuple(sorted({str(item).strip().lower() for item in raw if str(item).strip()}))
    if len(tags) > MAX_TAGS or any(len(item) > 64 for item in tags):
        raise ValueError("tags are out of bounds")
    return tags

def content_digest(content: CommunityContent) -> str:
    payload = "|".join((content.content_id, content.author_id, content.kind.value, content.text, ";".join(content.tags), ";".join(content.source_refs)))
    return sha256(payload.encode()).hexdigest()

def bounded_evidence(values: tuple[str, ...] | list[str] = ()) -> tuple[str, ...]:
    result = tuple(str(item).strip() for item in values if str(item).strip())
    if len(result) > MAX_EVIDENCE:
        raise ValueError("evidence is out of bounds")
    return result
