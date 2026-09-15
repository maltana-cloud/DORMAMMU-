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

Categories 1–26 are complete and locked at their defined repository boundaries. Category 27, DORMAMMU Ecosystem Evolution, has been implemented on `codex/category-27-ecosystem-evolution` and is pending CI/merge verification. Production readiness remains unclaimed.

## Implemented foundation

- core state/tasks/planning/events/permissions;
- security, containment, owner control, cryptographic recovery;
- truth/research/provenance and provider routing;
- capability/resource contracts, registry, discovery/evaluation, lifecycle, canary;
- conservative local CPU/RAM/storage/GPU inventory;
- bounded resource reservation and durable lease infrastructure;
- bounded operation execution and verification;
- executive objective/goal/task contracts and evidence-backed executive understanding;
- SQLite-backed operational telemetry and derived health;
- evidence-backed knowledge synthesis with verified-claim gating, provenance preservation, contradiction detection, uncertainty, and executive-requirement filtering;
- bounded real-world action contracts and execution with permission, provider health/fallback, dry-run, idempotency, verification, and audit;
- bounded multi-source continuous discovery with source health/failure isolation, scope/freshness gates, deduplication, ranking, and scheduling boundary;
- controlled learning/evolution with evidence gates, versioned promotion, durable records, and rollback;
- ecosystem-level evolution orchestration with finite proposal/candidate budgets and capability-health gating.

## Repository map

- `core/` — foundational state, tasks, planning, events, permissions, engine.
- `devintel/runtime/` — composition root.
- `devintel/security/` and `devintel/modules/security/` — security/containment/recovery.
- `devintel/executive/` — objective understanding and task decomposition/execution.
- `devintel/operations/` — bounded execution and telemetry.
- `devintel/capabilities/` — capability/resource discovery, inventory, lifecycle, canary, decisions.
- `devintel/modules/research/` — research, provenance, synthesis.
- `devintel/providers/` — provider contracts/routing/live adapters.
- `devintel/actions/` — provider-independent bounded real-world action execution.
- `devintel/intelligence/` — bounded global multi-source discovery.
- `devintel/ecosystem/` — bounded ecosystem evolution orchestration.
- `DORMAMMU_CHARTER.md` — architectural constitution.
- `DORMAMMU_STATUS.md` — current human-readable state.
- `DORMAMMU_PROJECT_STATE.json` — machine-readable checkpoint.
- `DORMAMMU_CAPABILITY_MATRIX.md` — detailed capability matrix.
- `DORMAMMU_ENGINEERING_MAP.md` — this control plane.

Legacy `DEVINTEL_*` names and the `devintel/` namespace remain only where compatibility requires them. Do not perform a blind rename.

## How the implemented pieces connect

Current bounded path:
`OBJECTIVE → GOAL UNDERSTANDING → EVIDENCE/SYNTHESIS WHEN AVAILABLE → TASK DECOMPOSITION → CAPABILITY DECISION → RESOURCE DECISION → PERMISSION → LIFECYCLE/CANARY WHEN NEEDED → ACT → MEASURE → VERIFY → RECORD`

Discovery path:
`GLOBAL DISCOVERY → SCOPE/FRESHNESS GATES → DEDUP/RANK → RESEARCH/VERIFY → KNOWLEDGE SYNTHESIS → EXECUTIVE REQUIREMENTS`

Action path:
`ACTION SPEC → PERMISSION → PROVIDER HEALTH → DETERMINISTIC ROUTE → ACT → VERIFY → AUDIT`

Evolution path:
`VERIFIED OUTCOMES → LEARNING PROPOSALS → BOUNDED CANDIDATES → CAPABILITY HEALTH → INDEPENDENT EVALUATION → VERSIONED PROMOTION → MONITOR → ROLLBACK IF NEEDED`

Broader target:
`OBJECTIVE → UNDERSTAND → DECOMPOSE → EVIDENCE SYNTHESIS → CAPABILITY DISCOVERY → MODEL/AGENT SELECTION → SPECIALIST COLLABORATION → EXECUTE → VERIFY → REFLECT → LEARN → EVOLVE → OUTCOME`

Capability expansion:
`DISCOVER GAP → DEFINE CONTRACT → ISOLATE → PERMISSION → SECURITY CHECK → BUILD/INTEGRATE → TEST → VERIFY → REGISTER/VERSION → CANARY → MONITOR → KEEP OR ROLLBACK`

## Current build order

### 1. Foundation — locked
Protect core authority, security, truth, owner control, recovery, auditability, modularity, backward compatibility, capability/resource discovery, lifecycle, canary, and rollback.

### 2. Bounded operating path — locked
Capability/resource decisions connect to permission, lifecycle/canary, action execution, verification, telemetry, and recording.

### 3. Executive cognition — locked
Objective understanding, explicit task decomposition, evidence-backed requirements, and scope/dependency validation exist without pretending that model output is authority or truth.

### 4. Operational telemetry — locked
Execution observations are durable and feed operational health and canary handling.

### 5. Evidence-backed knowledge synthesis — locked
Verified claims are normalized and synthesized conservatively with provenance, contradictions, uncertainty, and executive filtering.

### 6. Real-world action boundary — locked
Authorized actions have stable contracts, deterministic provider fallback, dry-run, idempotency, explicit verification, and tamper-evident audit.

### 7. Global discovery boundary — locked
Continuous discovery is externally driven and bounded; source failures, scope, freshness, deduplication, ranking, and scheduling are explicit.

### 8. Ecosystem evolution — implemented, pending CI/merge verification
Verified learning proposals can be evaluated and promoted into reversible scoped versions under bounded policy and capability-health gates. Protected surfaces remain outside evolution.

### 9. Ω Unknown Frontier
Future work is selected from verified capability gaps rather than a fixed assumption about what the ecosystem must become. Candidate work must preserve the locked constitution and be implemented, tested, integrated, verified, documented, and reversible where applicable.

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

A meaningful capability needs a stable contract, runtime integration where applicable, happy/failure tests, security/permission checks, provenance where relevant, observability, resource/cost controls, safe degradation/rollback where relevant, compatibility/migration handling, successful CI, truthful state, and capability-appropriate integration evidence.

## Remaining open capability surface

- post-merge operational verification for capabilities whose environments require it;
- broad trusted external capability acquisition;
- complete model/agent/specialist routing;
- production-grade heterogeneous compute orchestration;
- complete communication/community ecosystem;
- full creation/distribution/awareness/monetization loop;
- controlled reflection/learning expansion;
- model training/evolution at ecosystem scale;
- future capabilities discovered through the Ω Unknown Frontier.

## North Star

“Complete” means the current North Star operating loop is implemented, integrated, verified, observable, deployable under authorized conditions, and capable of safe extension without changing the foundational constitution. The foundation is locked in direction and boundaries, not frozen in functionality.

**Final rule:** Do not build what the architecture merely describes. Build what the repository can prove.
