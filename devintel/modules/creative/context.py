"""Adapters that feed existing intelligence layers into creative planning."""
from __future__ import annotations
from dataclasses import dataclass
from ...executive.cognition import CognitiveState, CoreCognition
from ..language import LanguageIntelligence, LanguageUnderstanding
from ..research import SynthesisResult
from .contracts import CreativeBrief

@dataclass(frozen=True)
class CreativeContext:
    brief_digest: str
    language: LanguageUnderstanding
    cognition: CognitiveState | None
    evidence_signal_count: int
    contradictions: int
    capability_ids: tuple[str, ...]
    resource_ids: tuple[str, ...]

class CreativeContextAdapter:
    """Compose existing language/research/cognition signals without granting authority."""
    def __init__(self, language: LanguageIntelligence | None = None, cognition: CoreCognition | None = None) -> None:
        self.language = language or LanguageIntelligence(); self.cognition = cognition or CoreCognition()
    def build(self, brief: CreativeBrief, *, scope_id: str = "creative", synthesis: SynthesisResult | None = None, known_capabilities: tuple[str, ...] = (), known_resources: tuple[str, ...] = (), known_limits: tuple[str, ...] = ()) -> CreativeContext:
        from .contracts import brief_digest
        understanding = self.language.understand(f"{brief.purpose}. Audience: {brief.audience}")
        state = None
        signals = contradictions = 0
        if synthesis is not None:
            state = self.cognition.from_synthesis(scope_id, synthesis, known_capabilities=known_capabilities, known_resources=known_resources, known_limits=known_limits)
            signals, contradictions = len(synthesis.signals), len(synthesis.contradictions)
        return CreativeContext(brief_digest(brief), understanding, state, signals, contradictions, tuple(known_capabilities), tuple(known_resources))
