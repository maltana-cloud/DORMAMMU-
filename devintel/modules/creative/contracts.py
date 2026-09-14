"""Contracts for bounded creative planning and quality evaluation.

Creative intelligence produces plans and evaluation records. It does not grant
publishing, spending, execution, or platform authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from typing import Tuple


MAX_TEXT = 16_384
MAX_ITEMS = 64


class AssetKind(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    GAME = "game"
    EDUCATION = "education"
    PRODUCT = "product"


class CreativeStatus(str, Enum):
    PROPOSED = "proposed"
    READY_FOR_CREATION = "ready_for_creation"
    NEEDS_REVIEW = "needs_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class CreativeBrief:
    purpose: str
    audience: str
    asset_kind: AssetKind
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    success_criteria: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for value in (self.purpose, self.audience):
            if not value or len(value.strip()) > MAX_TEXT:
                raise ValueError("brief fields must be non-empty and bounded")
        if len(self.constraints) > MAX_ITEMS or len(self.success_criteria) > MAX_ITEMS:
            raise ValueError("brief item collections are bounded")


@dataclass(frozen=True)
class CreativePlan:
    brief_digest: str
    concept: str
    steps: Tuple[str, ...]
    risks: Tuple[str, ...] = field(default_factory=tuple)
    status: CreativeStatus = CreativeStatus.PROPOSED

    def __post_init__(self) -> None:
        if len(self.concept.strip()) == 0 or len(self.concept) > MAX_TEXT:
            raise ValueError("concept must be non-empty and bounded")
        if len(self.steps) == 0 or len(self.steps) > MAX_ITEMS:
            raise ValueError("plan must contain a bounded number of steps")
        if len(self.risks) > MAX_ITEMS:
            raise ValueError("risks are bounded")
        if len(self.brief_digest) != 64:
            raise ValueError("brief_digest must be a SHA-256 hex digest")


@dataclass(frozen=True)
class CreativeEvaluation:
    plan_digest: str
    criterion_scores: Tuple[Tuple[str, float], ...]
    defects: Tuple[str, ...] = field(default_factory=tuple)
    status: CreativeStatus = CreativeStatus.NEEDS_REVIEW

    def __post_init__(self) -> None:
        if len(self.plan_digest) != 64:
            raise ValueError("plan_digest must be a SHA-256 hex digest")
        if not self.criterion_scores or len(self.criterion_scores) > MAX_ITEMS:
            raise ValueError("criterion scores must be bounded and non-empty")
        for name, score in self.criterion_scores:
            if not name or not 0.0 <= score <= 1.0:
                raise ValueError("criterion scores must be in [0, 1]")
        if len(self.defects) > MAX_ITEMS:
            raise ValueError("defects are bounded")


def brief_digest(brief: CreativeBrief) -> str:
    payload = "\n".join((brief.purpose.strip(), brief.audience.strip(), brief.asset_kind.value, *brief.constraints, *brief.success_criteria))
    return sha256(payload.encode("utf-8")).hexdigest()


def plan_digest(plan: CreativePlan) -> str:
    payload = "\n".join((plan.brief_digest, plan.concept, *plan.steps, *plan.risks, plan.status.value))
    return sha256(payload.encode("utf-8")).hexdigest()
