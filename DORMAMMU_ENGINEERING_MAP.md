# DORMAMMU — ENGINEERING CONTROL PLANE

> Canonical builder entry point. Repository code, tests, CI, and verified runtime behavior are the engineering source of truth.

## Mission

DORMAMMU is a coordinated autonomous intelligence and ecosystem platform whose mission is to turn verified understanding into useful action and sustainable value while preserving truth, safety, owner authority, modularity, resilience, and continuous evolution.

**Product principle:** MANUFACTURE USEFULNESS, NOT ENGAGEMENT.

Core action loop:
`REQUEST → UNDERSTAND → PLAN → PERMISSION CHECK → SECURITY CHECK → ACT → MEASURE → VERIFY → RECORD → IMPROVE`

## Non-negotiable boundaries

- Intelligence is not authority.
- Capability is not authority.
- Model output is not truth.
- External information is untrusted until validated.
- `IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`.
- No unrestricted self-modification.
- No automatic paid acquisition.
- No CAPTCHA, quota, licensing, OAuth, payment, identity-verification, exchange-control, or platform-security bypass.
- Owner authority, secrets, audit integrity, containment, and recovery remain protected.
- New capabilities are additive, bounded, testable, observable, versioned, and reversible.
- Never fake users, votes, followers, streams, engagement, identity, or community activity.

Read `AGENTS.md`, `DORMAMMU_CHARTER.md`, and `AI_WORKING_RULES.md` before architectural changes.

## Status vocabulary

`PLANNED / DESIGNED / PARTIAL / IMPLEMENTED / TESTED / VERIFIED / DEPLOYED / BLOCKED`

Documentation is not implementation proof. Unit tests are not automatically production verification.

## Current repository checkpoint

Knowledge synthesis feature was merged to `main` as `19d4d3ae0682cf4a34f80db0a0da7d6fd6379aae` after feature-head CI run **#603** passed on `c78dfeae0f5de5f027d8fd1f44333d902948e694`. Post-merge main CI has not yet been independently observed, so the synthesis milestone remains `TESTED` rather than `VERIFIED`.

## Implemented/tested foundation

- core state/tasks/planning/events/permissions;
- security, containment, owner control, cryptographic recovery;
- truth/research/provenance and provider routing;
- capability/resource contracts, registry, discovery/evaluation, lifecycle, canary;
- conservative local CPU/RAM/storage/GPU inventory;
- bounded resource reservation with fail-closed capacity;
- bounded operation execution and verification;
- explicit executive objective/goal/task contracts and dependency/scope validation;
- SQLite-backed operational telemetry and derived health;
- telemetry-fed operational health path into the existing canary/lifecycle boundary;
- evidence-backed knowledge synthesis with verified-claim gating, provenance preservation, contradiction detection, uncertainty, and executive-requirement filtering.

## Repository map

- `core/` — foundational state, tasks, planning, events, permissions, engine.
- `devintel/runtime/` — composition root.
- `devintel/security/` and `devintel/modules/security/` — security/containment/recovery.
- `devintel/executive/` — objective understanding and task decomposition/execution.
- `devintel/operations/` — bounded execution and telemetry.
- `devintel/capabilities/` — capability/resource discovery, inventory, lifecycle, canary, decisions.
- `devintel/modules/research/` — research, provenance, synthesis.
- `devintel/providers/` — provider contracts/routing/live adapters.
- `devintel/modules/education/` — education lifecycle.
- `DORMAMMU_CHARTER.md` — architectural constitution.
- `DORMAMMU_STATUS.md` — current human-readable state.
- `DORMAMMU_PROJECT_STATE.json` — machine-readable checkpoint.
- `DORMAMMU_CAPABILITY_MATRIX.md` — detailed capability matrix.
- `DORMAMMU_ENGINEERING_MAP.md` — this control plane.

Legacy `DEVINTEL_*` names and the `devintel/` namespace remain only where compatibility requires them. Do not perform a blind rename.

## How the implemented pieces connect

Current bounded path:
`OBJECTIVE → GOAL UNDERSTANDING → TASK DECOMPOSITION → CAPABILITY DECISION → RESOURCE DECISION → PERMISSION → LIFECYCLE/CANARY WHEN NEEDED → ACT → MEASURE → VERIFY → RECORD`

Evidence path now available:
`RESEARCH → VERIFY EVIDENCE → NORMALIZE CLAIMS → SYNTHESIZE → CHECK CONTRADICTIONS → EXPOSE PROVENANCE/UNCERTAINTY → EXECUTIVE REQUIREMENTS`

Broader target:
`OBJECTIVE → UNDERSTAND → DECOMPOSE → EVIDENCE SYNTHESIS → CAPABILITY DISCOVERY → MODEL/AGENT SELECTION → SPECIALIST COLLABORATION → EXECUTE → VERIFY → REFLECT → LEARN → OUTCOME`

Capability expansion:
`DISCOVER GAP → DEFINE CONTRACT → ISOLATE → PERMISSION → SECURITY CHECK → BUILD/INTEGRATE → TEST → VERIFY → REGISTER/VERSION → CANARY → MONITOR → KEEP OR ROLLBACK`

Controlled improvement:
`OBSERVE → MEASURE → IDENTIFY WEAKNESS → RESEARCH → EXPERIMENT → EVALUATE → VERIFY → APPROVE → INTEGRATE → MONITOR`

## Current build order

### 1. Foundation — locked direction

Protect core authority, security, truth, owner control, recovery, auditability, modularity, backward compatibility, capability/resource discovery, lifecycle, canary, and rollback.

### 2. Bounded operating path — tested

Capability and resource decisions are connected to permission, lifecycle/canary, action execution, verification, and recording.

### 3. Executive cognition — tested foundation

`Objective`, `GoalUnderstanding`, `TaskSpec`, and `ExecutivePlan` exist. The default interpreter intentionally normalizes explicit fields only. Task decomposition is explicit and scope/dependency checked.

### 4. Operational telemetry — tested foundation

Execution observations are durable in SQLite and include duration, success, verification, stage, and resource reservation metadata. Health requires a minimum sample count. Healthy active capabilities can be verified without reactivation; unhealthy active health goes through existing canary/lifecycle handling.

### 5. Evidence-backed knowledge synthesis — tested

`devintel/modules/research/synthesis.py` combines verified claims conservatively, canonicalizes provenance, detects contradictions after normalization, exposes uncertainty, excludes unsupported inputs, and prevents contradictory/low-confidence signals from becoming executive requirements. Runtime integration is present. Feature-head CI #603 passed; post-merge main CI remains to be observed.

### 6. Next: evidence-backed executive intelligence

Build the adapter between synthesis and executive planning:

`SYNTHESIS → REQUIREMENTS/SUCCESS CRITERIA → SCOPE/DEPENDENCIES → PLAN → BOUNDED EXECUTION → VERIFY`

It must preserve provenance and uncertainty and reject contradictory/insufficient evidence. Evidence must never grant authority.

### 7. Durable resource leases

Move active resource reservations from process-local memory toward durable, scoped, crash-safe leases with expiry, release, recovery, and audit semantics before heterogeneous multi-host orchestration.

### 8. Trusted external capability/resource expansion

External scouts/adapters must be evaluated for provenance/trust, license/terms, dependencies, compatibility, security, performance, resources, cost, permissions, maintainability, rollback, and observability before use.

### 9. Ecosystem expansion

Progressively integrate communication, education, creation, software/tool building, media, community, opportunity/product/service discovery, analytics, distribution, and monetization behind the same boundaries.

### 10. Advanced evolution

Later add training/evaluation, AI/ML research, controlled self-improvement, new-domain expansion, and resource optimization. Privileged systems remain explicitly bounded and reviewable.

## Capability acquisition policy

Preferred order:
`EXISTING → REUSE → TRUSTED OPEN SOURCE → FREE PROVIDER → LOCAL COMPUTE → BUILD/FINE-TUNE → LOW-COST PAID → EXPENSIVE`

Discovery itself never installs, executes, authenticates, spends money, or grants authority.

## Builder procedure

1. **RECONSTRUCT** — read this map, charter, status, state, relevant code/tests/history.
2. **INSPECT** — verify implementation rather than trusting claims.
3. **IDENTIFY** — find the highest-value dependency gap.
4. **DESIGN** — define the smallest stable contract.
5. **IMPLEMENT** — preserve boundaries and compatibility.
6. **TEST** — include success and failure paths.
7. **SECURITY CHECK** — authority, secrets, untrusted input, isolation, rollback.
8. **VERIFY** — integration evidence and CI.
9. **RECORD** — update status/state/matrix truthfully.
10. **CONTINUE** — choose the next unblocked dependency.

## Definition of done

A meaningful capability needs a stable contract, runtime integration, happy/failure tests, security/permission checks, provenance where relevant, observability, resource/cost controls, safe degradation/rollback where relevant, compatibility/migration handling, successful CI, truthful state, and capability-appropriate integration evidence.

## Not yet done

- post-merge verification of the synthesis merge checkpoint;
- evidence-backed executive requirements/success-criteria integration;
- arbitrary natural-language objective understanding/decomposition;
- durable resource leases;
- broad trusted external capability acquisition;
- complete model/agent/specialist routing;
- controlled reflection/learning loop;
- complete communication/community ecosystem;
- full creation/distribution/awareness/monetization loop;
- production-grade heterogeneous compute orchestration;
- model training/evolution at ecosystem scale.

## North Star

“Complete” means the current North Star operating loop is implemented, integrated, verified, observable, deployable under authorized conditions, and capable of safe extension without changing the foundational constitution. The foundation is locked in direction and boundaries, not frozen in functionality.

**Final rule:** Do not build what the architecture merely describes. Build what the repository can prove.
