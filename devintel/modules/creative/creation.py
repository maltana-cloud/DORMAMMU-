"""Translate verified creative specifications into host-routed generation requests."""
from __future__ import annotations
from dataclasses import dataclass
from ..providers.live import GenerationRequest
from .pipeline import CreativeResult

@dataclass(frozen=True)
class CreativeCreationRequest:
    provider_id: str
    generation: GenerationRequest
    plan_digest: str
    consistency: tuple[tuple[str, str], ...]

class CreativeCreationAdapter:
    """Build a generation request only; execution remains outside creative intelligence."""
    def build(self, result: CreativeResult, *, model: str = "", temperature: float = 0.2, max_tokens: int = 1024) -> CreativeCreationRequest:
        if not result.verification.passed:
            raise ValueError("creative result must pass verification before request construction")
        if result.provider.provider_id is None:
            raise RuntimeError("no approved compatible creative provider")
        consistency = result.plan.consistency
        metadata = {"creative_plan_digest": result.artifact.plan_digest, "asset_kind": result.brief.asset_kind.value}
        return CreativeCreationRequest(result.provider.provider_id, GenerationRequest(result.artifact.specification, model=model, temperature=temperature, max_tokens=max_tokens, metadata=metadata), result.artifact.plan_digest, (("style", consistency.style), ("character_identity", consistency.character_identity), ("environment", consistency.environment), ("resolution", consistency.resolution), ("fps", str(consistency.fps or "")), ("aspect_ratio", consistency.aspect_ratio), ("seed_strategy", consistency.seed_strategy), ("post_processing", ",".join(consistency.post_processing))))
