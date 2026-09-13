"""Health-gated canary evaluation with safe rollback."""
from __future__ import annotations

from dataclasses import dataclass
from .contracts import CapabilityStatus
from .lifecycle import CapabilityLifecycle


@dataclass(frozen=True)
class CanaryHealth:
    """Bounded health observations for one canary window."""

    healthy: bool
    success_rate: float
    error_rate: float
    latency_ms: float
    reason: str = ""


@dataclass(frozen=True)
class CanaryDecision:
    capability_id: str
    status: CapabilityStatus
    activated: bool
    rolled_back: bool
    reason: str


@dataclass(frozen=True)
class CanaryPolicy:
    min_success_rate: float = 0.99
    max_error_rate: float = 0.01
    max_latency_ms: float = 5000.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.min_success_rate <= 1.0:
            raise ValueError("min_success_rate must be between 0 and 1")
        if not 0.0 <= self.max_error_rate <= 1.0:
            raise ValueError("max_error_rate must be between 0 and 1")
        if self.max_latency_ms <= 0:
            raise ValueError("max_latency_ms must be positive")


class CanaryMonitor:
    """Evaluate canary health and fail closed through the lifecycle state machine."""

    def __init__(self, lifecycle: CapabilityLifecycle, policy: CanaryPolicy | None = None) -> None:
        self.lifecycle = lifecycle
        self.policy = policy or CanaryPolicy()

    def evaluate(self, capability_id: str, health: CanaryHealth) -> CanaryDecision:
        failures: list[str] = []
        if not health.healthy:
            failures.append("health check failed")
        if not 0.0 <= health.success_rate <= 1.0:
            failures.append("invalid success rate")
        elif health.success_rate < self.policy.min_success_rate:
            failures.append("success rate below canary threshold")
        if not 0.0 <= health.error_rate <= 1.0:
            failures.append("invalid error rate")
        elif health.error_rate > self.policy.max_error_rate:
            failures.append("error rate above canary threshold")
        if health.latency_ms < 0 or health.latency_ms > self.policy.max_latency_ms:
            failures.append("latency outside canary threshold")
        if failures:
            reason = "; ".join(failures)
            if health.reason.strip():
                reason = f"{reason}; {health.reason.strip()}"
            current = self.lifecycle.registry.get(capability_id)
            if current is None:
                raise KeyError(capability_id)
            if current.status is CapabilityStatus.CANARY:
                updated = self.lifecycle.rollback(capability_id, reason)
            elif current.status is CapabilityStatus.ACTIVE:
                updated = self.lifecycle.degrade(capability_id, reason)
                updated = self.lifecycle.rollback(capability_id, "automatic rollback after degradation: " + reason)
            else:
                raise RuntimeError("canary health can only be evaluated for CANARY or ACTIVE capabilities")
            return CanaryDecision(capability_id, updated.status, False, True, reason)
        current = self.lifecycle.registry.get(capability_id)
        if current is None:
            raise KeyError(capability_id)
        if current.status is not CapabilityStatus.CANARY:
            raise RuntimeError("successful canary health evaluation requires CANARY state")
        updated = self.lifecycle.activate(capability_id)
        return CanaryDecision(capability_id, updated.status, True, False, "canary health verified")
