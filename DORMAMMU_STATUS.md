# DORMAMMU STATUS

## Current Milestone
**Capability & Resource Discovery — controlled lifecycle + runtime integration**

## Truth Rule
This file describes repository state; implementation claims are based on code/tests/CI evidence, not documentation alone. The latest checkpoint remains **verification pending** until CI run 477 completes.

## Verified Foundations
- Core systems, plugin/specialist framework, orchestration, permissions, security/truth, autonomy, education, and provider routing remain in the repository.
- Live provider adapters exist for keyless Wikipedia retrieval and optional Gemini generation.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability discovery contracts, registries, deterministic evaluation gates, and free-first policy are implemented.

## Newly Implemented
- Controlled capability lifecycle state machine: `DISCOVERED → EVALUATED → APPROVED → REGISTERED → CANARY → ACTIVE`, with explicit degradation and rollback paths.
- Owner permission is required before lifecycle approval.
- Safe read-only local inventory for CPU, RAM, storage, and declared GPU resources.
- Runtime composition now owns capability/resource registries and the capability discovery service.
- Runtime exposes capability/resource observations to bounded autonomy as data-only observations.
- Runtime exposes discovery and inventory APIs without automatically installing, executing, authenticating, or granting authority.
- Regression tests cover lifecycle ordering, explicit approval, canary/activation/rollback, local inventory, and autonomy observation bridging.

## Important Repository Correction
A previous project-state record claimed runtime capability methods were present before they were actually in `devintel/runtime/app.py`. Repository inspection caught that inconsistency. The runtime integration is now implemented rather than merely documented.

## Known Gaps
- Latest CI for the newest checkpoint is still running; do not claim this checkpoint verified until it succeeds.
- No external capability marketplace/scout is enabled.
- Local inventory is intentionally conservative and does not invent GPU availability.
- Lifecycle records are currently in-memory; durable persistence is pending.
- Canary/rollback state transitions exist, but automated health-driven rollback orchestration is pending.
- Discovery results are available to autonomy, but observation-driven capability acquisition/planning is not yet autonomous.
- Wikipedia remains retrieval/snippet evidence, not a general web research engine.
- Gemini remains optional and requires an owner-supplied credential.

## Next Engineering Target
After CI verification: durable lifecycle/audit records, monitored canary health, and a bounded observation-driven capability decision path. External scouts remain disabled until those controls are verified.

## Completion Standard
Capability discovery is not complete until discovery, evaluation, permissions, security, compatibility, cost, resource requirements, lifecycle, observability, fallback, rollback, and integration are implemented and verified.

**Every AI working on DORMAMMU must leave a truthful, test-backed checkpoint.**
