"""Bounded read-only catalog scouts for legitimate capability discovery."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .contracts import CapabilityDescriptor, CapabilityRequirement, CapabilityScout
from .evidence import CapabilityEvidence


@dataclass(frozen=True)
class CatalogPolicy:
    timeout_seconds: float = 5.0
    max_bytes: int = 1_000_000
    allowed_hosts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0 or self.timeout_seconds > 30: raise ValueError("timeout_seconds must be between 0 and 30")
        if self.max_bytes <= 0 or self.max_bytes > 10_000_000: raise ValueError("max_bytes must be positive and bounded")


class JsonCatalogScout(CapabilityScout):
    """Convert a pre-fetched JSON catalog into untrusted capability candidates."""
    def __init__(self, payload: str, *, source: str, publisher: str, reference: str) -> None:
        self.payload = payload
        self.source = source
        self.publisher = publisher
        self.reference = reference

    def discover(self, requirement: CapabilityRequirement):
        document = json.loads(self.payload)
        entries = document.get("capabilities", document) if isinstance(document, dict) else document
        if not isinstance(entries, list): raise ValueError("catalog must contain a capabilities list")
        retrieved = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(self.payload.encode("utf-8")).hexdigest()
        results = []
        for raw in entries:
            if not isinstance(raw, dict): continue
            try:
                candidate = CapabilityDescriptor(
                    capability_id=str(raw["capability_id"]), name=str(raw["name"]), version=str(raw["version"]),
                    interfaces=tuple(raw.get("interfaces", ())), provider=str(raw["provider"]), license=str(raw["license"]),
                    cost=float(raw.get("cost", 0)), currency=str(raw.get("currency", "USD")),
                    permissions=tuple(raw.get("permissions", ())), dependencies=tuple(raw.get("dependencies", ())),
                    metadata=dict(raw.get("metadata", {})),
                    evidence=(CapabilityEvidence(self.source, retrieved, self.publisher, self.reference, digest, str(raw.get("terms_url", "")), bool(raw.get("signature_verified", False))),),
                )
            except (KeyError, TypeError, ValueError):
                continue
            if requirement.capability_id and raw.get("capability_id") not in {requirement.capability_id, "*"}:
                if requirement.required_interfaces and not set(requirement.required_interfaces).intersection(candidate.interfaces): continue
            results.append(candidate)
        return tuple(results)


class HttpJsonCatalogScout(JsonCatalogScout):
    """Read-only HTTPS catalog adapter with explicit host and response-size bounds."""
    def __init__(self, url: str, *, source: str, publisher: str, policy: CatalogPolicy | None = None) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname: raise ValueError("catalog URL must use HTTPS")
        self.url = url
        self.policy = policy or CatalogPolicy()
        if self.policy.allowed_hosts and parsed.hostname not in self.policy.allowed_hosts: raise PermissionError("catalog host is not allowlisted")
        super().__init__("{}", source=source, publisher=publisher, reference=url)

    def discover(self, requirement: CapabilityRequirement):
        request = Request(self.url, headers={"Accept": "application/json", "User-Agent": "DORMAMMU-capability-scout/1"}, method="GET")
        with urlopen(request, timeout=self.policy.timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" not in content_type: raise ValueError("catalog response is not JSON")
            body = response.read(self.policy.max_bytes + 1)
        if len(body) > self.policy.max_bytes: raise ValueError("catalog response exceeds size limit")
        self.payload = body.decode("utf-8")
        return super().discover(requirement)
