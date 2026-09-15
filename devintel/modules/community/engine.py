"""Bounded social/community understanding, demand detection, and planning."""
from __future__ import annotations
from dataclasses import dataclass
import re
from .contracts import CommunityContent, CommunityMember, CommunityPlan, CommunitySignal, ContentKind, ResponseDraft, SignalKind, MAX_CONTENT_ITEMS, MAX_MEMBERS, bounded_evidence, normalize_tags, normalize_text

_NEED = ("need", "looking for", "how do i", "help", "problem", "struggling", "want to")
_QUESTION = ("?", "how", "what", "why", "where", "when", "can someone")
_OPPORTUNITY = ("opportunity", "hiring", "job", "collaboration", "partner", "available", "launch")
_RISK = ("scam", "fraud", "warning", "danger", "risk", "unsafe", "breach")

@dataclass(frozen=True)
class CommunityObservation:
    community_id: str
    members: tuple[CommunityMember, ...]
    content: tuple[CommunityContent, ...]

class CommunityIntelligence:
    """Turns untrusted community observations into bounded, advisory signals."""
    def observe(self, community_id: str, members: tuple[CommunityMember, ...], content: tuple[CommunityContent, ...]) -> CommunityObservation:
        community_id = str(community_id).strip()
        if not community_id: raise ValueError("community_id is required")
        if len(members) > MAX_MEMBERS or len(content) > MAX_CONTENT_ITEMS: raise ValueError("community observation is out of bounds")
        member_ids = {m.member_id for m in members}
        if len(member_ids) != len(members): raise ValueError("duplicate member_id")
        normalized = tuple(CommunityContent(c.content_id.strip(), c.author_id.strip(), c.kind, normalize_text(c.text), normalize_tags(c.tags), bounded_evidence(c.source_refs)) for c in content)
        if any(not c.content_id or not c.author_id for c in normalized): raise ValueError("content identity is required")
        if any(c.author_id not in member_ids for c in normalized): raise ValueError("content author is not in observation")
        return CommunityObservation(community_id, members, normalized)

    def analyze(self, observation: CommunityObservation) -> tuple[CommunitySignal, ...]:
        signals = [self._signal(observation.community_id, c) for c in observation.content]
        return tuple(sorted((s for s in signals if s is not None), key=lambda s: (s.relevance, s.confidence, s.content_id), reverse=True))

    def plan(self, observation: CommunityObservation, *, max_drafts: int = 8) -> CommunityPlan:
        if max_drafts < 0 or max_drafts > 32: raise ValueError("max_drafts is out of bounds")
        signals = self.analyze(observation)
        drafts = []
        for signal in signals[:max_drafts]:
            if signal.kind in {SignalKind.RISK}: continue
            source = next(c for c in observation.content if c.content_id == signal.content_id)
            purpose = "answer_question" if signal.kind is SignalKind.QUESTION else "address_need" if signal.kind is SignalKind.NEED else "acknowledge_opportunity" if signal.kind is SignalKind.OPPORTUNITY else "contribute_context"
            drafts.append(ResponseDraft(f"draft:{source.content_id}", source.content_id, self._draft_text(source, signal), purpose, signal.evidence))
        next_steps = ("verify claims before publishing", "apply distribution and permission policy", "retain provenance and uncertainty", "measure outcomes after authorized publication")
        return CommunityPlan(observation.community_id, signals, tuple(drafts), next_steps)

    def _signal(self, community_id: str, content: CommunityContent) -> CommunitySignal | None:
        text = content.text.lower()
        if any(token in text for token in _RISK): kind = SignalKind.RISK
        elif any(token in text for token in _OPPORTUNITY): kind = SignalKind.OPPORTUNITY
        elif any(token in text for token in _NEED): kind = SignalKind.NEED
        elif any(token in text for token in _QUESTION): kind = SignalKind.QUESTION
        else: kind = SignalKind.DISCUSSION
        words = re.findall(r"[a-z0-9']+", text)
        relevance = min(1.0, 0.25 + min(len(words), 80) / 160)
        confidence = 0.55 if kind is SignalKind.DISCUSSION else 0.70
        return CommunitySignal(community_id, content.content_id, kind, f"Detected {kind.value} signal in community content", relevance, confidence, content.source_refs)

    @staticmethod
    def _draft_text(content: CommunityContent, signal: CommunitySignal) -> str:
        if signal.kind is SignalKind.QUESTION: return "I can help investigate this question. The relevant claim should be verified before I give a definitive answer."
        if signal.kind is SignalKind.NEED: return "I understand the need. I can help break the problem down and identify verified options."
        if signal.kind is SignalKind.OPPORTUNITY: return "This may be worth evaluating. We should verify the opportunity and its terms before taking action."
        return "Thanks for raising this. I can add verified context where useful."
