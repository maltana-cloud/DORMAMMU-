# DORMAMMU STATUS

## Current Milestone
**Categories 25–26 — IMPLEMENTED / PENDING FINAL CI + MERGE.** DORMAMMU now has a bounded real-world action execution boundary and an externally driven continuous multi-source discovery boundary. Both preserve the existing permission, security, provenance, audit, provider, runtime, and owner-control architecture.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence.

## Category Status
1–24. COMPLETE / LOCKED
25. Real-World Action Infrastructure — IMPLEMENTED / PENDING FINAL CI + MERGE
26. Global Intelligence & Continuous Discovery — IMPLEMENTED / PENDING FINAL CI + MERGE

## Category 25 Scope
Category 25 adds provider-independent real-world action contracts and a bounded execution facade. Actions are explicit capabilities and never authorities. Execution requires the existing `PermissionPolicy`; high-risk actions remain owner-gated. Providers are host-registered, health-checked, isolated, and tried deterministically. Dry-run mode provides a no-side-effect path. Idempotency prevents duplicate execution within one executor instance, while external adapters remain responsible for platform-specific idempotency across process recovery.

### Category 25 Completion Evidence
- stable `ActionSpec`, `ActionOutcome`, `ActionStatus`, and `ActionProvider` contracts;
- bounded host-controlled `ActionRegistry`;
- existing centralized permission policy reused rather than duplicated;
- high-risk owner approval remains mandatory;
- deterministic provider selection and legitimate fallback;
- provider health and result validation;
- explicit dry-run/no-side-effect mode;
- process-local content-bound idempotency fingerprint and completed-result reuse;
- explicit optional verification hook; execution success is not silently treated as verified truth;
- tamper-evident audit events for denial, dry-run, success, and terminal failure;
- provider failures and malformed results isolated;
- regression coverage for permission, fallback, idempotency, dry-run, verification, and malformed output.

## Category 26 Scope
Category 26 adds bounded continuous multi-source discovery rounds. “Continuous” is an externally driven recurring boundary, not an unrestricted background loop. Sources are replaceable capabilities; source health/failure is isolated; observations are scope-bound, freshness-bounded, deterministic, deduplicated, and remain untrusted until the established research verification/knowledge pipeline accepts them.

### Category 26 Completion Evidence
- bounded configurable source count and observation count;
- deterministic source ordering;
- explicit recurring interval and `due()` scheduler boundary;
- scope/query validation;
- source health checks and failure isolation;
- stale/future/wrong-scope observations rejected;
- deterministic duplicate resolution and ranking;
- bounded round output with explicit rejected count;
- regression coverage for bounds, deduplication, source failures, freshness, scope isolation, and scheduling boundary;
- no authentication, authority grant, publication, payment, installation, or execution derived from discovery.

## Security Boundary
`IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`

Action providers and discovery sources are capabilities, not authorities. External content and provider output remain untrusted until independently validated. Existing owner-control, permission, security, provenance, audit, and recovery boundaries remain authoritative.

## Production Boundary
Categories 25–26 do **not** claim production deployment. Category 25 does not provide platform-specific credentials, OAuth/session management, distributed exactly-once side effects, external transactional rollback, or unrestricted financial/deployment authority. Category 26 does not provide global internet coverage, unrestricted background polling, distributed scheduling/locking, source reputation/fact-checking, or automatic truth admission. Those require explicit infrastructure and operational evidence.

## Post-Roadmap Engineering
Categories 1–24 remain complete/locked at their defined repository boundaries. Categories 25–26 are active until final CI, merge, and post-merge verification. Category 27 — DORMAMMU Ecosystem Evolution — follows after these checkpoints are verified.

New capabilities must preserve the locked foundation and use established discovery, permission, security, testing, verification, versioning, canary, monitoring, fallback, and rollback rules.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, preserve this truthful checkpoint, and build forward from the repository rather than treating prior chat history as authoritative.
