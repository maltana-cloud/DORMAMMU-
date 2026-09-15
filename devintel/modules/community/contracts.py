"""Bounded contracts for social/community intelligence."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Mapping

MAX_MEMBERS = 100_000
MAX_MESSAGES = 10_000
MAX_TEXT = 4_096
MAX_TAGS = 32

class MemberKind(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    SYSTEM = "system"

class ContentKind(str, Enum):
    POST = "post"
    COMMENT = "comment"
    ANNOUNCEMENT = "announcement"

class ActionKind(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    QUEUE = "queue"
    PUBLISH = "publish"

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
class CommunityAction:
    action_id: str
    actor_id: str
    kind: ActionKind
    content_id: str = ""
    target: str = ""

@dataclass(frozen=True)
class CommunitySignal:
    community_id: str
    content_id: str
    signal: str
    confidence: float
    evidence: tuple[str, ...] = ()

@dataclass(frozen=True)
class CommunityPolicyDecision:
    allowed: bool
    reason: str
    requires_owner_approval: bool
    risk: str

def normalized_text(text: object) -> str:
    value = " ".join(str(text).split())
    if not value or len(value) > MAX_TEXT:
        raise ValueError("content text is empty or out of bounds")
    return value

def normalized_tags(values: Mapping[str, object] | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    raw = values.keys() if isinstance(values, Mapping) else values
    tags = tuple(sorted({str(v).strip().lower() for v in raw if str(v).strip()}))
    if len(tags) > MAX_TAGS or any(len(tag) > 64 for tag in tags):
        raise ValueError("tags are out of bounds")
    return tags

def content_digest(content: CommunityContent) -> str:
    payload = "|".join((content.content_id, content.author_id, content.kind.value, content.text, ";".join(content.tags), ";".join(content.source_refs)))
    return sha256(payload.encode()).hexdigest()
