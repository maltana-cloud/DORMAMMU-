# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Matrix checkpoint:** main commit `6d061efae23d98d689058c01ce65cb63c56ba647` passed GitHub Actions run **575**. Telemetry branch CI run **573** also passed.

| Capability | Status | Implementation path | Tests | CI evidence | Dependencies | Security status | Known limitations | Next action | Version | Last verified commit |
|---|---|---|---|---|---|---|---|---|---|---|
| DORMAMMU identity migration | IMPLEMENTED | `DORMAMMU_CHARTER.md`; `DORMAMMU_*`; `devintel/runtime/` | `tests/test_capability_runtime.py`; compatibility coverage | #507 success | legacy namespace compatibility | Protected; no blind rename | `devintel/` and legacy `DEVINTEL_*` names remain intentionally | Remove legacy naming only where compatibility permits | 1.0 | `a3c730...` |
| Capability & Resource Discovery | TESTED | `devintel/capabilities/contracts.py`, `discovery.py`, `registry.py`, `decision.py` | `tests/test_capability_discovery.py`, `test_capability_decision.py`, runtime tests | #521/#522 success | registries, evaluator, runtime | Advisory only; no install/auth/execute | External scouts are not yet production-trusted | Add provenance-aware trusted scouts and integration adapters | 1.0 | `cae16d7...` |
| Resource / Compute Management | TESTED | `devintel/capabilities/resources.py`, `inventory.py`; runtime integration; bounded operations | `tests/test_resource_manager.py`, `test_capability_runtime.py`, `test_bounded_operation.py` | #535/#537 success | resource registry, local inventory, permission boundary | Fail-closed capacity; no provisioning/spending | Reservations are in-memory; no multi-host scheduler or durable lease system | Add durable scoped leases | 1.0 | `d0eaa5d...` |
| Domain Intelligence | TESTED | `devintel/modules/`, research, education, specialists | domain/module test suite | #507 success | core runtime, providers | Domain modules remain behind core/security boundaries | Broad domain coverage is uneven | Connect domain services to executive operating path | 1.0 | `a3c730...` |
| Ecosystem Awareness | PARTIAL | research/providers, publishing/product-facing modules | research/provider/publishing tests | #507 success | live adapters, truth/provenance | External content treated as untrusted | No complete cross-platform awareness loop | Build source aggregation + freshness/importance pipeline | 0.1 | `a3c730...` |
| Knowledge synthesis / cross-domain reasoning | PARTIAL | research/truth + autonomy/planning foundations | research/truth/autonomy tests | #507 success | verified evidence, planning, provider routing | Truth/provenance boundaries exist | No complete cross-domain synthesis engine | Implement evidence-backed synthesis contract | 0.1 | `a3c730...` |
| Executive cognition foundation | TESTED | `devintel/executive/contracts.py`; `devintel/executive/engine.py`; runtime | `tests/test_executive_engine.py` | #554/#555 success | bounded operations; capability/resource decision; permission; canary; verification | Explicit scope and per-capability approval | Default interpreter only normalizes explicit fields; decomposition is explicit | Add evidence-backed goal understanding and routing | 0.1 | `58a3afe...` |
| Operational telemetry | TESTED | `devintel/operations/telemetry.py`; `devintel/operations/bounded.py`; runtime | `tests/test_operational_telemetry.py`; bounded/runtime integration | #573/#575 success | bounded execution, SQLite, canary/lifecycle | Evidence only; no authority grant; minimum sample gate | Resource leases remain in-memory; telemetry health is derived from operation observations | Add durable resource leases and richer provider/resource metrics | 0.1 | `6d061ef...` |
| Full autonomous operating path | PARTIAL | `devintel/executive/`; `devintel/operations/`; `devintel/capabilities/`; runtime | executive + bounded + telemetry tests | #575 success | executive cognition; capability/resource management; telemetry; permission; canary; verification | Bounded and permission-gated | No arbitrary natural-language decomposition, dynamic routing, reflection/learning, or full ecosystem loop | Add evidence-backed synthesis, routing, reflection and durable leases | 0.3 | `6d061ef...` |
| Model Training & Evolution | PLANNED | architecture direction only | no dedicated implementation test | baseline only | datasets, compute, evaluation, safety governance | No unrestricted self-modification | Training/evolution loop not built | Define isolated training/evaluation contracts | 0.1 | `a3c730...` |
| Engineering / Coding Intelligence | PARTIAL | existing developer/domain modules and tool-builder direction | existing module tests | #507 success | core, tools, sandbox execution | Generated code must remain controlled | No complete coding-agent loop | Connect coding specialist to bounded execution + verification | 0.1 | `a3c730...` |
| Language & Speech Intelligence | PLANNED | no complete subsystem identified in current foundation | no dedicated implementation test | baseline only | model/provider routing, platform I/O | Must isolate microphone/audio credentials and platform authority | No production speech subsystem | Define language/speech provider contracts | 0.1 | `a3c730...` |
| Opinion Intelligence | PLANNED | charter intent only | no dedicated implementation test | baseline only | truth/provenance, discourse modeling | Fact/opinion/speculation distinction required | No dedicated opinion engine | Define opinion/evidence/uncertainty contract | 0.1 | `a3c730...` |
| Platform Identity & Account Management | PARTIAL | control/security foundations; platform adapters | security/control/provider tests | #507 success | authentication/session/capability boundaries | `IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY` | No complete multi-platform identity plane | Implement scoped account/session contracts | 0.1 | `a3c730...` |
| Community Intelligence | PARTIAL | community/publishing-facing modules and architecture | existing module tests | #507 success | platform adapters, identity, memory, policy | No fake engagement; platform rules preserved | No complete autonomous community loop | Build isolated community state + participation policy | 0.1 | `a3c730...` |
| Crypto / Blockchain Ecosystem | PLANNED | domain scope only | no dedicated implementation test | baseline only | market data, security, account controls | No unrestricted trading/withdrawal authority | No dedicated production subsystem | Define read-only intelligence contracts first | 0.1 | `a3c730...` |
| Creative / Media Systems | PARTIAL | creative/media architecture and modules where present | existing module tests where applicable | #507 success | provider routing, resource management, verification | Generation is not quality proof | No complete media production pipeline | Define asset/project/quality verification contracts | 0.1 | `a3c730...` |
| Music / Audio | PLANNED | architecture intent only | no dedicated implementation test | baseline only | media/audio providers, resource management | External audio providers remain untrusted capabilities | No complete music/audio system | Define audio capability contracts | 0.1 | `a3c730...` |
| Gaming | PLANNED | architecture intent only | no dedicated implementation test | baseline only | creative/media, runtime, resource management | Game actions must remain scoped | No complete gaming subsystem | Define game/runtime capability boundary | 0.1 | `a3c730...` |
| Business / Revenue / Reinvestment | PARTIAL | opportunity/business modules and owner control | existing business/monitoring tests | #507 success | analytics, owner control, financial boundaries | Spending and commercial authority protected | No autonomous commercial execution | Implement value/revenue/cost outcome contracts | 0.1 | `a3c730...` |
| Owner Identity / Zero-Trust Recovery | TESTED | `devintel/modules/security/recovery.py`, `orchestrator.py`, owner control | security recovery tests | #507 success | external secret provisioning; security state | HMAC authorization with tamper/expiry/replay protection; no backdoor | Secret provisioning external; asymmetric provider optional | Harden provisioning and recovery verification | 1.0 | `a3c730...` |
| Self-Model / Resilience / Continuous Evolution | PARTIAL | autonomy, monitoring, security, recovery, capability lifecycle | autonomy/security/monitoring tests | #507 success | observations, metrics, recovery, controlled improvement | Unrestricted self-modification prohibited | No ecosystem-scale self-improvement loop | Implement measured reflection/outcome learning without privileged self-editing | 0.1 | `a3c730...` |

## Highest-priority gaps

1. **Evidence-backed knowledge synthesis:** normalize verified claims, preserve provenance, expose uncertainty, detect contradictions, and produce evidence-linked synthesis for executive requirements.
2. **Durable resource leases:** operation telemetry is durable, but active resource reservations remain in-memory.
3. **Evidence-backed goal understanding:** the default interpreter normalizes explicit fields; it does not infer arbitrary natural-language goals safely.
4. **Model/agent/specialist routing:** executive tasks do not yet dynamically select the best available intelligence capability.
5. **Trusted external capability acquisition:** scouts/adapters need provenance, license/terms, security, compatibility, permission, resource, cost, rollback, and observability controls end-to-end.
6. **Reflection/learning:** telemetry exists, but no controlled outcome-learning loop yet turns evidence into bounded improvement.

## Blocked vs not built

The matrix does not mark missing credentials or platform verification as software failures. Those become `BLOCKED` only when the software is ready and an external owner/platform action is genuinely required.

At this checkpoint no listed major capability is marked `BLOCKED`; several are simply not built yet.

## Verification rule

`TESTED` means meaningful repository tests exist and have passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
