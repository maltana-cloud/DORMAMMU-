# DORMAMMU — ENGINEERING CONTROL PLANE

> **Canonical builder entry point.** Read this before changing DORMAMMU.
>
> Repository code, tests, CI, and verified runtime behavior are the engineering source of truth. Documentation describes intent and state; it never substitutes for implementation evidence.

## 1. What DORMAMMU Is

DORMAMMU is a coordinated autonomous intelligence and ecosystem platform. It is not a single bot, chatbot, news feed, trading bot, or collection of unrelated agents.

Its permanent mission is:

> **Turn verified understanding into useful action and sustainable value while preserving truth, safety, owner authority, modularity, resilience, and continuous evolution.**

Product principle: **MANUFACTURE USEFULNESS, NOT ENGAGEMENT.**

The long-term ecosystem loop is:

`OBSERVE → DISCOVER → UNDERSTAND → VERIFY → IDENTIFY DEMAND → CREATE → DISTRIBUTE → CREATE AWARENESS → MONETIZE → MEASURE → EVOLVE`

The action contract is:

`REQUEST → UNDERSTAND → PLAN → PERMISSION CHECK → SECURITY CHECK → ACT → VERIFY → RECORD → IMPROVE`

## 2. What Must Not Be Broken

These are architectural boundaries, not optional features:

- Intelligence is not authority.
- Capability is not authority.
- Model output is not truth.
- External information is untrusted until validated.
- `IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`.
- No unrestricted self-modification.
- No automatic paid acquisition.
- No bypass of quotas, CAPTCHAs, licensing, platform controls, or authorization.
- Owner authority must remain protected.
- Security must remain independently enforceable.
- Recovery must remain protected and auditable.
- New capabilities must be additive, bounded, testable, observable, versioned, and reversible.
- Backward compatibility must be preserved where the repository explicitly provides a compatibility boundary.
- Never fake users, votes, followers, streams, engagement, identity, or community activity.

Read `DORMAMMU_CHARTER.md`, `AGENTS.md`, and `AI_WORKING_RULES.md` before architectural changes.

## 3. Status Vocabulary

Never collapse these states:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

A document saying something exists is not proof that it exists. A unit test passing is not automatically production verification. A production claim requires integration evidence appropriate to the capability.

## 4. Current Verified Foundation

The current verified code checkpoint is commit `58a3afe21a18c7a826da3f635c73da6ec244a625`.

GitHub Actions test run **#555** completed successfully for that commit.

Verified/tested foundation areas include:

- core engine, state, tasks, planning, events, and permission boundaries;
- specialist/domain framework and bounded autonomy;
- research/truth/provenance mechanisms;
- education lifecycle;
- provider-neutral routing with live adapter boundaries;
- canonical `DORMAMMURuntime` with `DEVINTELRuntime` retained only as compatibility alias;
- capability/resource contracts, registries, discovery, evaluation gates, and local inventory;
- controlled capability lifecycle;
- lifecycle event persistence;
- cryptographic recovery authorization;
- canary health evaluation and bounded rollback;
- bounded capability decision path;
- bounded resource reservation and fail-closed capacity handling;
- executive objective/goal understanding contracts;
- dependency-checked, scope-checked task decomposition;
- executive execution connected to the bounded operating path.

Important limitations remain: external capability acquisition is intentionally not autonomous; canary health still needs real operational metrics; durable operational outcomes/resource leases are not complete; live provider coverage is limited; and the full autonomous ecosystem is not yet complete.

## 5. Repository Map

### Foundational authority

- `core/` — low-level contracts, state, tasks, planning, events, permissions, engine.
- `devintel/modules/security/` — security policy, containment, orchestration, recovery, truth boundaries.
- `devintel/control/` — owner-control policy and observation/control boundary.
- `devintel/runtime/` — composition root and runtime integration.

### Executive and execution

- `devintel/executive/` — objective understanding contracts, task decomposition, bounded executive execution.
- `devintel/autonomy/` — finite bounded autonomous behavior.
- `devintel/operations/` — bounded end-to-end operating path.

### Intelligence

- `devintel/modules/research/` — research pipeline, storage, provenance verification.
- `devintel/modules/education/` — educational lifecycle and policy.
- `devintel/providers/` — provider abstractions, routing, and live adapters.
- `modules/` — higher-level product-facing modules such as publishing.

### Capability and resources

- `devintel/capabilities/contracts.py` — stable capability/resource/evaluation contracts.
- `devintel/capabilities/registry.py` — capability/resource registration.
- `devintel/capabilities/discovery.py` — bounded discovery and evaluation.
- `devintel/capabilities/inventory.py` — conservative local resource inventory.
- `devintel/capabilities/resources.py` — bounded resource decisions and in-memory reservations.
- `devintel/capabilities/lifecycle.py` — explicit lifecycle state machine.
- `devintel/capabilities/store.py` — append-only SQLite lifecycle event store.
- `devintel/capabilities/canary.py` — canary health and rollback boundary.
- `devintel/capabilities/decision.py` — bounded decision path: use existing, request approval, or record gap.

### Truthful project state

- `DORMAMMU_CHARTER.md` — permanent architectural and operating constitution.
- `DORMAMMU_ENGINEERING_MAP.md` — this builder control plane.
- `DORMAMMU_PROJECT_STATE.json` — machine-readable state checkpoint.
- `DORMAMMU_STATUS.md` — concise human-readable status.
- `DORMAMMU_CAPABILITY_MATRIX.md` — detailed capability matrix.
- `README.md` — public project orientation.
- `AGENTS.md` — repository-level engineering/autonomy rules.
- `AI_WORKING_RULES.md` — rules for AI builders working on the repository.

Legacy `DEVINTEL_*` files/names may remain where needed for compatibility. Do not perform a blind rename.

## 6. How the Pieces Connect Today

The implemented bounded path is:

`OBJECTIVE → GOAL UNDERSTANDING → TASK DECOMPOSITION → CAPABILITY DECISION → RESOURCE DECISION → PERMISSION → LIFECYCLE/CANARY WHEN NEEDED → ACT → VERIFY → RECORD`

The intended broader mechanism remains:

`OBJECTIVE → GOAL UNDERSTANDING → TASK DECOMPOSITION → CAPABILITY DISCOVERY → MODEL/AGENT SELECTION → SPECIALIST COLLABORATION → EXECUTION → VERIFICATION → REFLECTION → LEARNING → OUTCOME`

Capability expansion follows:

`DISCOVER GAP → DEFINE CONTRACT → ISOLATE → PERMISSION → SECURITY CHECK → BUILD/INTEGRATE → TEST → VERIFY → REGISTER/VERSION → CANARY → MONITOR → KEEP OR ROLLBACK`

Controlled improvement follows:

`OBSERVE → MEASURE → IDENTIFY WEAKNESS → RESEARCH → EXPERIMENT → EVALUATE → VERIFY → APPROVE → INTEGRATE → MONITOR`

No step may silently bypass the authority, security, truth, audit, or recovery boundaries.

## 7. Current Build Order

Build in dependency order, not by excitement or feature popularity.

### A. Foundation — locked direction

Protect and regression-test:

1. Core state/task/planning contracts.
2. Permission and owner authority.
3. Security, containment, and recovery.
4. Truth/provenance/verification.
5. Auditability and observability.
6. Runtime composition.
7. Capability/resource discovery and lifecycle.
8. Canary and rollback boundaries.
9. Backward compatibility.

### B. Bounded operating path — implemented/tested

The first bounded path now exists and composes:

`GOAL → REQUIREMENTS → CAPABILITY DECISION → RESOURCE DECISION → PERMISSION CHECK → APPROVAL WHEN REQUIRED → LIFECYCLE → CANARY → ACT → VERIFY → RECORD`

It fails safely when capability/resource/permission/verification prerequisites are unavailable.

### C. Executive cognition foundation — implemented/tested

The repository now has explicit `Objective`, `GoalUnderstanding`, `TaskSpec`, and `ExecutivePlan` contracts plus a bounded execution engine. The default interpreter intentionally performs only explicit-field normalization. Task decomposition is explicit and scope/dependency validated.

### D. Operational telemetry and durable outcomes — next engineering target

Connect real execution observations to:

- success/error rate;
- latency;
- verification outcome;
- resource usage/reservation;
- lifecycle state;
- provider health;
- operation outcome.

Feed these measurements into canary evaluation and durable outcome records. Do not accept caller-supplied health as the sole source of truth for production decisions.

### E. Evidence-backed executive intelligence

Then add trustworthy goal understanding from structured/unstructured requests, requirements extraction, evidence-backed success criteria, model/agent routing, specialist collaboration, and reflection — all through bounded contracts.

### F. Trusted capability/resource expansion

Add external scouts and integration adapters only after provenance, source trust, license/terms, dependencies, compatibility, security, permissions, resource limits, cost, rollback, and observability are enforced end-to-end.

### G. Ecosystem capabilities

Progressively integrate research, communication, education, creation, software/tool building, media, community participation, opportunity discovery, product/service discovery, analytics, distribution, and monetization — each behind the same contracts.

### H. Advanced evolution

Later integrate model training/evaluation, AI/ML research, controlled self-improvement, new-domain expansion, and resource optimization. Privileged/self-modifying infrastructure must remain explicitly bounded and reviewable.

## 8. Capability Acquisition Policy

Preferred order:

`EXISTING → REUSE → TRUSTED OPEN SOURCE → FREE PROVIDER → LOCAL COMPUTE → BUILD/FINE-TUNE → LOW-COST PAID → EXPENSIVE`

Discovery must never itself install, execute, authenticate, spend money, or grant authority.

Every candidate should be evaluated for:

- provenance/trust;
- license and terms;
- dependencies;
- security;
- compatibility;
- performance;
- resource requirements;
- cost;
- required permissions;
- maintainability;
- rollback/recovery.

## 9. Builder Operating Procedure

For every task:

1. **RECONSTRUCT** — read this map, charter, status, project state, relevant code, tests, and recent history.
2. **INSPECT** — verify what actually exists. Search for implementations, not merely claims.
3. **IDENTIFY** — state the exact gap and its dependencies.
4. **DESIGN** — define the smallest stable contract that fits the architecture.
5. **IMPLEMENT** — make the change modular and backward-compatible.
6. **TEST** — add meaningful unit and integration tests, including failure paths.
7. **SECURITY CHECK** — verify authority, permissions, untrusted-input handling, secrets, isolation, and rollback.
8. **VERIFY** — run the relevant test suite and CI; distinguish test evidence from production evidence.
9. **RECORD** — update machine-readable and human-readable project state truthfully.
10. **CONTINUE** — choose the next highest-value unblocked dependency; do not start unrelated projects.

If a conflict or uncertainty is found, stop guessing. Preserve existing work, document the conflict, and resolve it deliberately.

## 10. Definition of Done

A subsystem is not complete because its classes exist.

For a meaningful capability, completion requires:

- clear purpose and stable contract;
- implementation wired into the correct owner/runtime boundary;
- happy-path and failure-path tests;
- permission and security checks;
- provenance/truth handling where information is involved;
- observability/auditability appropriate to risk;
- resource/cost limits where relevant;
- safe degradation and rollback where relevant;
- backward compatibility or an explicitly versioned migration;
- successful CI;
- truthful status update;
- integration evidence appropriate to the claim.

## 11. What Is Not Yet Done

Do not tell a builder that DORMAMMU is a finished autonomous ecosystem.

Not yet complete:

- arbitrary natural-language objective understanding and decomposition;
- real operational canary telemetry;
- durable operation outcome/resource lease storage;
- broad trusted external capability scouting/acquisition;
- complete model/agent selection and specialist collaboration loop;
- evidence-backed cross-domain synthesis;
- complete autonomous communication/community ecosystem;
- full creation/distribution/awareness/monetization loop;
- production-grade resource orchestration across diverse compute;
- controlled model training/evolution/self-improvement at ecosystem scale.

These are targets, not hidden implementations.

## 12. North Star and the Meaning of “End”

The project does not have a fake final feature list. The North Star is a durable operating system for useful intelligence that can safely expand into new capabilities without repeatedly rebuilding its foundations.

“End-to-end complete” means that the current North Star operating loop is implemented, integrated, verified, observable, deployable under authorized conditions, and capable of safely evolving through the extension procedure. New capabilities can then continue to be added without changing the foundational constitution.

The foundation is **locked in direction and boundaries**, not frozen in functionality.

## 13. Final Rule

**Do not build what the architecture merely describes. Build what the repository can prove.**

Every builder should be able to enter this repository cold, understand what DORMAMMU is, determine what is real, identify the next dependency, implement it without weakening the foundation, and leave a verifiable checkpoint for the next builder.
