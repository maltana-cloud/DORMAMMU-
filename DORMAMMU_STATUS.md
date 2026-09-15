# DORMAMMU STATUS

## Current Milestone
**Ω.2 — INTEGRATED FRONTIER CONTROL PLANE — COMPLETE / LOCKED.** The repository now has a connected, bounded control-plane layer for durable frontier work, worker leases, retry/dead-letter isolation, scope-bound resource budgets, opaque credential references, and evidence-backed reflection. The control plane is integrated into the DORMAMMU composition root and preserves existing mission, provider, capability, action, telemetry, knowledge, and evolution boundaries.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence.

## Category Status
1–27. COMPLETE / LOCKED
Ω.1. BOUNDED DISTRIBUTED MISSION COORDINATION — COMPLETE / LOCKED
Ω.2. INTEGRATED FRONTIER CONTROL PLANE — COMPLETE / LOCKED
Ω. Unknown Frontier — remains open

## Ω.2 — Integrated Frontier Control Plane
Implemented in `devintel/frontier/control.py` and composed by `devintel/runtime/app.py`.

### Completion Evidence
- durable SQLite frontier queue with deterministic priority ordering;
- atomic worker claims with finite leases and expiry takeover;
- live-lease enforcement prevents expired/stale workers from finalizing work;
- bounded retries terminate in explicit dead-letter state;
- expired work at its attempt limit is dead-lettered during recovery;
- scope-bound resource budgets use atomic reservation/release operations;
- opaque provider credential references define a host-owned resolution boundary without storing secret values;
- deterministic, deduplicated evidence-backed reflection records persist outcomes, lessons, and uncertainty;
- runtime composition root exposes the frontier control plane and supports a configurable durable store path while retaining memory-only defaults;
- integration coverage verifies runtime composition, persistence across runtime instances, job completion, and reflection persistence;
- feature CI run **#1228** passed completely, including the full repository `Run tests` step and job cleanup;
- PR **#91** was merged as squash commit `22b03ec885361eb2a8cecf87d70fa52426ddb483`.

## Architectural Relationship to the Five Frontier Areas
1. **Real external-world capability:** credential references provide secret indirection while existing action/provider permission and verification remain authoritative. Actual OAuth/token/session acquisition still requires host/provider infrastructure and real credentials.
2. **Distributed production infrastructure:** queueing, leases, retry isolation, dead-lettering, and resource budgets provide repository-level primitives. Multi-host production requires an appropriate database/queue topology and operational evidence.
3. **Capability/provider ecosystem:** existing capability discovery/acquisition/lifecycle remains authoritative; this layer coordinates durable work without automatic installation or authorization.
4. **Long-term autonomous intelligence:** reflection persistence provides a durable outcome/lesson boundary with evidence and uncertainty; it does not autonomously rewrite protected code, security, or authority surfaces.
5. **Production proof:** local CI proves repository behavior only. Real providers/credentials, multi-host operation, heterogeneous compute, live communication/distribution, monitoring, backup/restore, load/failure testing, canary deployment, and rollback evidence require authorized operational environments.

## Security Boundary
`IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`

Ω.2 adds coordination and evidence storage only. A worker lease, resource budget, credential reference, queue item, or reflection record does not grant permissions, credentials, capability activation, spending, external access, or owner/security authority.

## Production Boundary
**Production readiness remains NOT_CLAIMED.** Repository-side engineering is implemented and verified, but external operational evidence has not been fabricated or implied.

## Next Boundary
**Ω — Unknown Frontier remains open.** Re-audit the merged repository and select the next capability from verified remaining gaps, user value, dependencies, security, resources, and architectural leverage. Do not treat Ω.2 as the end of DORMAMMU's development.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, preserve this truthful checkpoint, and build forward from the repository rather than treating prior chat history as authoritative.
