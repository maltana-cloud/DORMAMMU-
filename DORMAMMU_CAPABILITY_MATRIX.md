# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Matrix checkpoint:** bounded autonomous operating, durable resource leases, trusted capability admission, bounded catalog scouting, model/agent/specialist routing, controlled outcome learning, bounded natural-language intake, provider-backed semantic interpretation, production capability-source configuration, runtime cognition integration, deterministic semantic safety evaluation, and the first bounded ecosystem-awareness aggregation layer are merged on `main`.

| Capability | Status | Implementation path | Tests | CI evidence | Dependencies | Security status | Known limitations | Next action | Version | Last verified commit |
|---|---|---|---|---|---|---|---|---|---|---|
| DORMAMMU identity migration | IMPLEMENTED | `DORMAMMU_CHARTER.md`; `DORMAMMU_*`; `devintel/runtime/` | compatibility coverage | successful CI | legacy namespace compatibility | Protected; no blind rename | legacy names remain intentionally | Remove legacy naming where compatibility permits | 1.0 | `a3c730...` |
| Capability & Resource Discovery | IMPLEMENTED | `devintel/capabilities/` discovery, evidence, acquisition, catalog, sources | discovery/acquisition/provenance/catalog/source/lifecycle/runtime tests | PR #51 CI passed | registries, provenance, evaluator, lifecycle, canary | Fail-closed strict provenance; no automatic trust/install | real sources still require legitimate explicit configuration | Validate configured sources operationally | 1.3 | `5a1dde...` |
| Resource / Compute Management | VERIFIED | `devintel/capabilities/resources.py`, `leases.py`, `inventory.py` | resource/lease/runtime tests | successful CI | resource registry, durable lease store, local inventory | fail-closed capacity; no provisioning/spending | no distributed scheduler | Add richer metrics/scheduling | 1.1 | `11d3eb5...` |
| Domain Intelligence | TESTED | `devintel/modules/` research, education, specialists | domain/module suite | successful CI | core runtime, providers | bounded modules | coverage uneven | Connect more domain services | 1.0 | `d73d6b6...` |
| Ecosystem Awareness | PARTIAL | `devintel/modules/growth/awareness.py` + growth contracts/engine | `tests/test_awareness_aggregation.py` + growth tests | CI evidence pending for latest direct commits | awareness observations, provenance, growth policy | HTTPS evidence only; scoped/bounded; no distribution authority | no live multi-source adapter or publishing loop yet | Connect approved source adapters and freshness/importance feeds | 0.2 | `1809416...` |
| Knowledge synthesis / cross-domain reasoning | TESTED | `devintel/modules/research/synthesis.py`; runtime | synthesis/runtime/security tests | successful CI | verified claims, provenance | contradictions/uncertainty preserved | not full reasoning | Add broader evidence composition | 0.2 | `d73d6b6...` |
| Executive cognition foundation | TESTED | `devintel/executive/` contracts/engine/evidence | executive tests | successful CI | bounded operations, capability/resource decision | explicit scope/approval | no arbitrary high-impact goal inference | Integrate semantic interpreter behind NL boundary | 0.1 | `7adad2d...` |
| Model / Agent / Specialist Routing | VERIFIED | `devintel/executive/routing.py` | routing/outcome-aware tests | PR #54 CI passed | registered specialists, health, approval, explicit requirements, verified outcomes | selection is not authority; learned preference cannot override hard gates | deterministic/local; no autonomous enrollment | Add broader provider binding/scheduling later | 1.1 | `ec62eae...` |
| Controlled reflection / outcome learning | IMPLEMENTED | `devintel/autonomy/learning.py`, `learning_store.py` | outcome learning/routing tests | latest integration CI evidence pending | verified same-scope outcomes, durable store | reversible proposals only | no unrestricted policy mutation | Verify end-to-end runtime integration | 1.1 | `ec62eae...` |
| Outcome-aware routing integration | IMPLEMENTED | `devintel/executive/outcome_routing.py`, routing preference signal | `tests/test_outcome_aware_routing.py` | latest integration CI evidence pending | durable proposals, registered specialists | advisory bounded scoring; hard gates dominate | service is bounded/local, not distributed scheduling | Integrate with production provider binding | 0.1 | `ec62eae...` |
| Bounded natural-language goal intake | IMPLEMENTED | `devintel/executive/nl_goal.py` | natural-language goal tests | PR #61 CI passed on head | explicit scope, interpreter contract | untrusted input; high-impact/ambiguity gates | provider behavior still needs operational evidence | Maintain semantic regression suite | 0.1 | `8af5af0...` |
| Semantic goal safety evaluation | VERIFIED | `devintel/executive/semantic_evaluation.py` | `tests/test_semantic_evaluation.py` | PR #62 head CI passed; no post-merge run exposed | bounded goal boundary | structured outcomes only; no authority/actions | real-provider operational evaluation remains follow-up | Gather legitimate provider/model evidence when available | 0.1 | `a190e11...` |
| Operational telemetry | TESTED | `devintel/operations/telemetry.py`; bounded/autonomy stores | telemetry/bounded/runtime/autonomy tests | successful CI | bounded execution, SQLite | evidence only | richer provider/resource metrics pending | Feed verified outcomes into runtime learning | 0.2 | `d73d6b6...` |
| Full autonomous operating path | VERIFIED | `devintel/autonomy/`, executive, operations, capabilities, routing, learning | autonomy/safety/cycle/runtime/routing/learning tests | earlier milestones passed CI; latest integration evidence pending | cognition, routing, resource/capability, permission, verification | bounded, permission-preflighted, finite, proposal-only improvement | distributed scheduling not built | Complete ecosystem and scheduling layers | 0.7 | `ec62eae...` |
| Production capability source configuration | IMPLEMENTED | `devintel/capabilities/sources.py` | `tests/test_capability_sources.py` | source PR CI passed | explicit source config, trusted evidence policy, HTTPS scout | disabled by default; host/timeout/size/trust gates | no source is silently trusted or installed | Operationally validate legitimate configured sources | 1.0 | `5a1dde...` |
| Model Training & Evolution | PLANNED | architecture direction | none | baseline | datasets, compute, evaluation, governance | no unrestricted self-modification | loop not built | Define isolated training/evaluation contracts | 0.1 | `d73d6b6...` |
| Engineering / Coding Intelligence | PARTIAL | developer/domain modules + bounded execution | existing tests | successful CI | core, tools, sandbox | generated code controlled | no complete coding-agent loop | Connect coding specialist to bounded execution | 0.1 | `d73d6b6...` |
| Language & Speech Intelligence | PLANNED | architecture intent | none | baseline | routing, providers, platform I/O | credentials isolated | no production speech subsystem | Define contracts | 0.1 | `d73d6b6...` |
| Opinion Intelligence | PLANNED | charter intent | none | baseline | truth/provenance, discourse | fact/opinion/speculation separated | no engine | Define contract | 0.1 | `d73d6b6...` |
| Platform Identity & Account Management | PARTIAL | control/security + adapters | security/control/provider tests | successful CI | auth/session/capability boundaries | identity separated from authority | no complete identity plane | Implement scoped account/session contracts | 0.1 | `d73d6b6...` |
| Community Intelligence | PARTIAL | community/publishing-facing modules | existing tests | successful CI | platform adapters, identity, memory, policy | no fake engagement | no autonomous community loop | Build isolated community state/policy | 0.1 | `d73d6b6...` |
| Crypto / Blockchain Ecosystem | PLANNED | domain scope | none | baseline | market data, security, account controls | no unrestricted trading/withdrawal | no subsystem | Define read-only intelligence contracts | 0.1 | `d73d6b6...` |
| Creative / Media Systems | PARTIAL | creative/media architecture/modules | applicable tests | successful CI | routing, resources, verification | generation not quality proof | no complete pipeline | Define asset/project/quality contracts | 0.1 | `d73d6b6...` |
| Music / Audio | PLANNED | architecture intent | none | baseline | media/audio providers, resources | providers untrusted | no system | Define contracts | 0.1 | `d73d6b6...` |
| Gaming | PLANNED | architecture intent | none | baseline | creative/media, runtime, resources | actions scoped | no subsystem | Define boundary | 0.1 | `d73d6b6...` |
| Business / Revenue / Reinvestment | PARTIAL | opportunity/business modules + owner control | existing tests | successful CI | analytics, owner control, financial boundaries | spending protected | no autonomous commercial execution | Implement outcome contracts | 0.1 | `d73d6b6...` |
| Owner Identity / Zero-Trust Recovery | TESTED | security recovery/orchestrator/owner control | recovery tests | successful CI | external secret provisioning | HMAC tamper/expiry/replay protection | provisioning external | Harden provisioning | 1.0 | `d73d6b6...` |
| Self-Model / Resilience / Continuous Evolution | PARTIAL | autonomy, monitoring, security, recovery, capability lifecycle | autonomy/security/monitoring tests | successful CI | observations, metrics, recovery, controlled improvement | proposal-only improvement | no general semantic autonomy | Integrate richer resilience | 0.3 | `ec62eae...` |

## Highest-priority gaps

1. **Broad ecosystem capabilities** — awareness is now bounded at the aggregation layer; communication, community, creation, distribution, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
2. **Distributed resource/provider scheduling** — current routing is deterministic/local.
3. **Production operational evidence** — real-provider/model-specific semantic evaluation and repository-wide evidence for earlier merged cognition work remain operational follow-ups.

## Blocked vs not built

Missing credentials or platform verification are not software failures. They become `BLOCKED` only when software is ready and an external owner/platform action is genuinely required.

At this checkpoint no listed major capability is `BLOCKED`; several remain not built.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
