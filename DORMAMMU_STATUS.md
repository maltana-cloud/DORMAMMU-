# DORMAMMU STATUS

## Current Milestone
**Ω — CONTINUOUS FRONTIER — ACTIVE.** Categories 1–27 and Ω.1–Ω.2 remain locked. Ω.3 persistent memory + dynamic owner authority + runtime cognition remain implemented/verified. The canonical architecture has now been explicitly extended to preserve continuous memory, dynamic owner authority, and a reusable authority boundary for future capabilities.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence. Requirements and designs must not be represented as implemented or production verified merely because they are documented.

## Requirement Truth Ladder
`REQUIREMENT → ARCHITECTURAL DESIGN → IMPLEMENTED → TESTED → PRODUCTION VERIFIED`

This ladder is the canonical distinction between planned capability, architecture, implementation, testing, and operational proof.

## Category Status
1–27. COMPLETE / LOCKED
Ω.1. BOUNDED DISTRIBUTED MISSION COORDINATION — COMPLETE / LOCKED
Ω.2. INTEGRATED FRONTIER CONTROL PLANE — COMPLETE / LOCKED
Ω.3. PERSISTENT MEMORY + DYNAMIC AUTHORITY + RUNTIME COGNITION — IMPLEMENTED / VERIFIED
Ω. Unknown Frontier — remains open

## Ω.3 — Persistent Memory, Dynamic Authority, Runtime Cognition
Implemented and integrated:
- `devintel/memory/store.py` provides durable scoped memory with episodic, semantic, procedural, entity, mission, and reflection kinds;
- memory preserves evidence references, confidence, timestamps, expiry, revisions, supersession, active state, deterministic identity, bounded retrieval, and scope isolation;
- `devintel/control/authority.py` provides owner-controlled capability rules with DENIED, APPROVAL_REQUIRED, and ALLOWED modes, versioning, optional expiry, fail-closed defaults, and durable revocation;
- runtime exposes persistent memory and authority stores and APIs;
- runtime restores bounded natural-language goal interpretation, outcome-aware specialist routing, durable learning-store lifecycle, and owner control-center composition that had remained stranded in an obsolete pre-Ω branch;
- runtime tests cover memory/authority persistence, expiry, revision/revocation, and cognition integration;
- feature CI passed for the final Ω.3 integration commit;
- PR **#92** added the memory/authority foundations and was merged as `102a0025c0487ed1dade618da06c95b86020fbf5`;
- PR **#93** integrated them with runtime cognition and was merged as `8c3cbe914ba05fd758c77a4fb0488ad493c681ba`;
- the superseded PR **#60** was closed after its verified runtime-cognition work was incorporated forward on current `main`.

## Canonical Future-Capability Boundary
DORMAMMU's authority is dynamic, owner-controlled, revocable, and extensible. Owner policy can be changed, restricted, placed behind approval, expired, or revoked after deployment without rebuilding DORMAMMU.

Future capabilities — including, where later authorized and safely implemented, email/account creation and management, email sending, public publishing, external communication, website management, deployments, service registration, financial/business operations, and capabilities not yet known — must use the same capability, permission, security, verification, and audit boundaries. No future capability may create a parallel authority path.

The governing flow is:
`DISCOVER NEED → DEFINE CAPABILITY → EVALUATE → REGISTER/IMPLEMENT → REQUEST AUTHORITY → LIVE PERMISSION CHECK → SECURITY CHECK → EXECUTE → VERIFY → RECORD`

Discovering a need or capability does not grant authority. Historical memory is not current authority. Capability discovery, provider identity, credentials, permissions, action execution, and owner authority remain separate boundaries.

## Architecture
Persistent memory is data, not authority. Authority is live policy, not memory. Capability discovery, provider identity, credentials, permissions, action execution, and owner authority remain separate boundaries. Owner policy can be changed, expired, or revoked after deployment without rebuilding DORMAMMU.

## Security Boundary
`IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`

Memory entries, learning records, leases, resource budgets, queue items, provider references, and authority rules do not by themselves grant credentials or unrestricted execution.

## Production Boundary
**Production readiness remains NOT_CLAIMED.** Repository CI proves repository behavior only. Real external accounts/credentials/OAuth sessions, third-party integrations, multi-host deployment, live communication, monitoring, backup/restore, load/failure evidence, heterogeneous compute, canary deployment, and rollback evidence require authorized operational environments.

## Documentation Checkpoint
The canonical architecture was updated to make the future-capability and dynamic-authority requirements explicit in `DORMAMMU_CHARTER.md` and `DORMAMMU_PROJECT_CHARTER.md`. These documentation changes establish requirements and architectural constraints; they do not falsely claim the future external capabilities are implemented.

## Next Boundary
**Ω — Unknown Frontier remains open.** Continue from the merged repository state. Re-audit actual implementation and select the next highest-leverage repository-solvable gap. Do not restart locked foundations or fabricate external operational proof.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, preserve truthful checkpoints, distinguish requirement/design/implementation/test/production evidence, and build forward from the repository rather than treating prior chat history as authoritative.
