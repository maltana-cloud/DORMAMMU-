# DORMAMMU STATUS

## Current Milestone
**DORMAMMU identity, architecture continuity, and extensibility lock**

## Completed
- [x] Master DORMAMMU architecture charter established.
- [x] README identifies DORMAMMU as the product/project identity.
- [x] Runtime now exposes the canonical `DORMAMMURuntime` name.
- [x] Legacy `DEVINTELRuntime` remains as a temporary compatibility alias so existing consumers are not broken during migration.
- [x] Python package metadata/docstring identifies DORMAMMU; the `devintel/` path remains temporarily for backward compatibility.
- [x] Architecture explicitly defines additive future capability support.
- [x] Future capabilities are required to use stable contracts, isolated state/lifecycle, permissions, security boundaries, tests, versioning, observability, fallback/degraded behavior, rollback, and migration paths where needed.
- [x] Capability/resource discovery is defined as a capability-gap process rather than uncontrolled installation.
- [x] Agents, models, providers, compute, tools, datasets, and platforms remain replaceable capabilities rather than authorities.
- [x] Existing provider routing remains bounded, health-aware, priority-based, and fallback-capable.

## Extensibility Lock

**Locked architecture does not mean frozen functionality.** DORMAMMU's principles, authority hierarchy, security constitution, owner-control boundaries, truth boundary, and recovery protections are stable. The capability surface remains intentionally open for future domains, agents, models, tools, providers, platforms, media systems, business systems, compute resources, and other useful capabilities.

New capability rule:

`DISCOVER GAP → DEFINE CONTRACT → ISOLATE → PERMISSION → SECURITY CHECK → BUILD/INTEGRATE → TEST → VERIFY → REGISTER/VERSION → CANARY → MONITOR → KEEP OR ROLLBACK`

A future feature must not require rewriting the DORMAMMU brain when a modular extension can solve the problem. Existing capabilities should continue operating while a new capability is introduced.

## Current Implementation Boundary

The public product identity is DORMAMMU. The repository still contains the historical `devintel/` implementation namespace because changing every import/path in one unverified operation would create unnecessary breakage. The namespace migration is therefore being performed incrementally with compatibility preserved.

This is deliberate migration state, not a second product identity.

## Verification

The identity migration changes were applied to the active `feat/dormammu-charter-and-capability-evolution` branch. Existing implementation behavior was preserved through the `DEVINTELRuntime = DORMAMMURuntime` compatibility alias.

A full repository test/CI verification is required before this milestone is merged. No test result is claimed here until CI exposes it.

## Next Action

Continue the DORMAMMU identity migration safely: rename remaining public documentation/status references, then add the capability/resource discovery implementation with contracts, registry, evaluation policy, scoped lifecycle, and tests. After that, connect the controlled provider layer to real research/model adapters and build the first real autonomous operating path.

## Non-Negotiable Rule

**Every AI that works on DORMAMMU must leave a truthful, test-backed checkpoint before stopping.**
