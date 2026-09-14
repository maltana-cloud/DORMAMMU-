"""Bounded language understanding and response shaping for DORMAMMU.

Text is untrusted input. This module produces deterministic understanding and
response constraints only; it never sends, authenticates, impersonates, or
grants communication authority.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

_MAX_TEXT = 16_384
_MAX_TOKENS = 512

@dataclass(frozen=True)
class LanguageUnderstanding:
    text_digest: str
    normalized_text: str
    tokens: tuple[str, ...]
    language_hint: str
    intents: tuple[str, ...]
    requires_confirmation: bool

@dataclass(frozen=True)
class ResponseConstraints:
    language: str
    max_chars: int = 4_096
    concise: bool = False
    preserve_uncertainty: bool = True

class LanguageIntelligence:
    """Deterministic, bounded text understanding and response constraints."""

    def understand(self, text: str) -> LanguageUnderstanding:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text.strip():
            raise ValueError("text is required")
        if len(text) > _MAX_TEXT:
            raise ValueError("text exceeds language bound")
        normalized = re.sub(r"\s+", " ", text.strip())
        tokens = tuple(re.findall(r"[\w']+", normalized.casefold()))[:_MAX_TOKENS]
        token_set = set(tokens)
        intents: list[str] = []
        if token_set & {"who", "what", "when", "where", "why", "how"} or "?" in normalized:
            intents.append("question")
        if token_set & {"build", "make", "create", "develop", "implement"}:
            intents.append("creation")
        if token_set & {"explain", "teach", "learn", "understand"}:
            intents.append("explanation")
        if token_set & {"find", "search", "look", "research"}:
            intents.append("research")
        high_impact = token_set & {"pay", "purchase", "transfer", "withdraw", "delete", "deploy", "publish", "send"}
        if high_impact:
            intents.append("high_impact_action")
        if not intents:
            intents.append("conversation")
        language = self._language_hint(token_set)
        digest = sha256(normalized.encode("utf-8")).hexdigest()
        return LanguageUnderstanding(digest, normalized, tokens, language, tuple(dict.fromkeys(intents)), bool(high_impact))

    def response_constraints(self, understanding: LanguageUnderstanding, *, max_chars: int = 4_096) -> ResponseConstraints:
        if not isinstance(understanding, LanguageUnderstanding):
            raise TypeError("understanding is required")
        if not 128 <= max_chars <= 16_384:
            raise ValueError("max_chars must be between 128 and 16384")
        return ResponseConstraints(
            language=understanding.language_hint,
            max_chars=max_chars,
            concise=len(understanding.tokens) > 80,
            preserve_uncertainty=True,
        )

    @staticmethod
    def _language_hint(tokens: set[str]) -> str:
        if tokens & {"se", "ni", "mo", "ko", "ore", "bawo", "padi"}:
            return "yo"
        if tokens & {"hola", "gracias", "como", "para", "que"}:
            return "es"
        if tokens & {"bonjour", "merci", "comment", "pour", "avec"}:
            return "fr"
        return "en"
