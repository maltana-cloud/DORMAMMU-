# DORMAMMU STATUS

## Current Milestone
**Foundation hardening — verified capability discovery, lifecycle, recovery, canary monitoring, and bounded decision path**

## Truth Rule
This file describes repository state; implementation claims require code, meaningful tests, and successful CI evidence. The latest verified checkpoint is commit `c02c54e6dcd7131a88aae72052f8e2cfc8bf5a1b`, validated by GitHub Actions run **504**.

## Verified Foundations
- Core systems, specialist/domain framework, orchestration, permissions, security/truth, autonomy, education, and provider routing remain in the repository.
- Live provider adapters exist for keyless Wikipedia retrieval and optional Gemini generation.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability/resource discovery, deterministic evaluation gates, free-first policy, controlled lifecycle, lifecycle event storage, safe local inventory, cryptographic recovery authorization, canary health monitoring/rollback, and bounded capability decisions are implemented and covered by tests.

## Verified Safety Boundaries
- Discovery does not install, execute, authenticate, or grant authority.
- Lifecycle transitions are explicit and state-validated; approval requires permission.
- Local resource inventory is read-only and conservative.
- Autonomy capability observations are data-only and do not grant authority.
- Recovery uses an externally supplied cryptographic secret, with tamper, expiry, and replay protection.
- Canary failure can produce bounded degradation/rollback rather than silent activation.
- No unrestricted self-modification or automatic paid acquisition.

## Repository Correction Completed
`DORMAMMU_PROJECT_STATE.json` had stale commit/CI information. It is now synchronized with the verified checkpoint and records the current capability statuses, verification facts, and known gaps.

## Remaining Engineering Work
- External capability scouts/marketplace discovery are intentionally disabled until trusted-source, licensing, dependency, security, compatibility, permission, and integration controls are wired end-to-end.
- Lifecycle storage is reusable and durable when configured with a persistent SQLite path; the runtime default remains `:memory:` for isolation and tests. Production deployment must explicitly configure durable storage.
- Canary monitoring currently evaluates supplied health observations; real operational metrics must be connected before claiming production autonomous rollout.
- The bounded capability decision engine can recommend `use_existing`, `request_approval`, or `record_gap`, but it does not autonomously acquire arbitrary external capabilities.
- Live external provider coverage remains intentionally limited; provider output is not itself truth.
- Full production autonomous ecosystem integration remains incomplete and must be built incrementally behind the locked safety/authority boundaries.

## Lock Criterion
The **foundational architecture** may be declared locked only after a final repository audit confirms that the Charter's identity, authority, security, truth, owner-control, recovery, permission, auditability, modularity, and safe-evolution boundaries are implemented, tested, CI-verified, and protected from accidental weakening. Locking the foundation does not mean future capabilities are finished; future capabilities must plug into these boundaries without rewriting them.

## Next Engineering Target
Perform the final Charter-to-code audit, close any remaining foundational security/authority/persistence gaps, verify the integrated paths, run CI, and record the resulting verified lock checkpoint. After foundation lock, continue with the first end-to-end bounded operating path.

**Every AI working on DORMAMMU must leave a truthful, test-backed checkpoint.**
