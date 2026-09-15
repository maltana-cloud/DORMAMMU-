"""Fail-closed policy for community interaction and publication proposals."""
from __future__ import annotations
from .contracts import CommunityPolicyDecision, CommunitySignal, SignalKind

class CommunityPolicy:
    def evaluate(self, signal: CommunitySignal, *, owner_approved: bool = False, platform_authorized: bool = False, publish: bool = False, is_reply: bool = True) -> CommunityPolicyDecision:
        if not 0 <= signal.confidence <= 1 or not 0 <= signal.relevance <= 1:
            return CommunityPolicyDecision(False, "invalid signal scores", False, "high")
        if not signal.community_id or not signal.content_id:
            return CommunityPolicyDecision(False, "community/content identity is required", False, "high")
        if signal.kind is SignalKind.RISK and not signal.evidence:
            return CommunityPolicyDecision(False, "risk signal requires evidence", True, "high")
        if not publish:
            return CommunityPolicyDecision(True, "analysis and drafting are permitted", False, "low")
        if not platform_authorized:
            return CommunityPolicyDecision(False, "platform authorization is required", True, "high")
        if not owner_approved:
            return CommunityPolicyDecision(False, "owner approval is required for external publication", True, "medium")
        if not is_reply and signal.kind is SignalKind.DISCUSSION:
            return CommunityPolicyDecision(False, "proactive engagement must provide material value", True, "medium")
        if signal.confidence < 0.60 or signal.relevance < 0.50:
            return CommunityPolicyDecision(False, "signal does not meet publication thresholds", False, "medium")
        return CommunityPolicyDecision(True, "publication proposal passed bounded policy", False, "medium")
