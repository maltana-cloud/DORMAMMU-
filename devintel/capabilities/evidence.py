"""Provenance evidence used to admit discovered capabilities safely."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse


@dataclass(frozen=True)
class CapabilityEvidence:
    """Auditable source metadata; evidence never grants authority by itself."""

    source: str
    retrieved_at: str
    publisher: str
    reference: str = ""
    integrity_hash: str = ""
    terms_url: str = ""
    signature_verified: bool = False

    def __post_init__(self) -> None:
        for value, name in ((self.source, "source"), (self.retrieved_at, "retrieved_at"), (self.publisher, "publisher")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        try:
            datetime.fromisoformat(self.retrieved_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("retrieved_at must be an ISO-8601 timestamp") from exc
        for value, name in ((self.reference, "reference"), (self.terms_url, "terms_url")):
            if value:
                parsed = urlparse(value)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError(f"{name} must be an absolute HTTP(S) URL")
        if self.integrity_hash and len(self.integrity_hash) < 16:
            raise ValueError("integrity_hash is too short")

    @property
    def trustworthy(self) -> bool:
        """Minimum provenance quality required for external admission."""
        return bool(self.reference or self.integrity_hash or self.signature_verified)
