# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Matrix checkpoint:** bounded autonomous operating, durable resource leases, trusted capability admission, bounded catalog scouting, model/agent/specialist routing, controlled outcome learning, bounded natural-language intake, production capability-source configuration, and bounded outcome-aware routing are merged on `main`. The latest outcome-aware routing merge is `ec62eaef6d544a192e99666deb5d9e6639b2aefb`; no workflow/status evidence is exposed for that commit through the available integration, so CI verification is not claimed for the latest merge.

| Capability | Status | Implementation path | Tests | CI evidence | Dependencies | Security status | Known limitations | Next action | Version | Last verified commit |
|---|---|---|---|---|---|---|---|---|---|---|
| DORMAMMU identity migration | IMPLEMENTED | `DORMAMMU_CHARTER.md`; `DORMAMMU_*`; `devintel/runtime/` | compatibility coverage | successful CI | legacy namespace compatibility | Protected; no blind rename | legacy names remain intentionally | Remove legacy naming where compatibility permits | 1.0 | `a3c730...` |
| Capability & Resource Discovery | IMPLEMENTED | `devintel/capabilities/` discovery, evidence, acquisition, catalog, sources | discovery/acquisition/provenance/catalog/source/lifecycle/runtime tests | PR #51 CI passed; latest source merge post-fix not exposed | registries, provenance, evaluator, lifecycle, canary | Fail-closed strict provenance; no automatic trust/install | real sources still require legitimate explicit configuration | Validate configured sources operationally | 1.3 | `5a1dde...` |
| Resource / Compute Management | VERIFIED | `devintel/capabilities/resources.py`, `leases.py`, `inventory.py` | resource/lease/runtime tests | successful CI | resource registry, durable lease store, local inventory | fail-closed capacity; no provisioning/spending | no distributed scheduler | Add richer metrics/scheduling | 1.1 | `11d3eb5...` |
| Domain Intelligence | TESTED | `devintel/modules/` research, education, specialists | domain/module suite | successful CI | core runtime, providers | bounded modules | coverage uneven | Connect more domain services | 1.0 | `d73d6b6...` |
| Ecosystem Awareness | PARTIAL | research/providers/publishing-facing modules | existing tests | successful CI | live adapters, truth/provenance | external content untrusted | no complete cross-platform loop | Build source aggregation + freshness/importance | 0.1 | `d73d6b6...` |
| Knowledge synthesis / cross-domain reasoning | TESTED | `devintel/modules/research/synthesis.py`; runtime | synthesis/runtime/security tests | successful CI | verified claims, provenance | contradictions/uncertainty preserved | not full reasoning | Add broader evidence composition | 0.2 | `d73d6b6...` |
| Executive cognition foundation | TESTED | `devintel/executive/` contracts/engine/evidence | executive tests | successful CI | bounded operations, capability/resource decision | explicit scope/approval | no arbitrary high-impact goal inference | Integrate semantic interpreter behind NL boundary | 0.1 | `7adad2d...` |
| Model / Agent / Specialist Routing | VERIFIED | `devintel/executive/routing.py` | `tests/test_specialist_routing.py`, outcome-aware routing tests | PR #54 CI passed; latest integration CI not exposed | registered specialists, health, approval, explicit requirements, verified outcomes | selection is not authority; learned preference cannot override hard gates | deterministic/local; no autonomous enrollment | Add broader provider binding/scheduling later | 1.1 | `ec62eae...` |
| Controlled reflection / outcome learning | IMPLEMENTED | `devintel/autonomy/learning.py`, `learning_store.py` | `tests/test_outcome_learning.py`, `tests/test_outcome_aware_routing.py` | latest integration CI not exposed | verified same-scope outcomes, durable store | reversible proposals only | no unrestricted policy mutation | Verify end-to-end runtime integration | 1.1 | `ec62eae...` |
| Outcome-aware routing integration | IMPLEMENTED | `devintel/executive/outcome_routing.py`, routing preference signal | `tests/test_outcome_aware_routing.py` | latest integration CI not exposed | durable proposals, registered specialists | advisory bounded scoring; hard gates dominate | service is bounded/local, not distributed scheduling | Integrate with production runtime/provider binding | 0.1 | `ec62eae...` |
| Bounded natural-language goal intake | IMPLEMENTED | `devintel/executive/nl_goal.py` | `tests/test_natural_language_goal.py` | PR #56 merge CI not exposed | explicit scope, interpreter contract | untrusted input; high-impact/ambiguity gates | deterministic parser only; not general semantic understanding | Add production semantic interpreter + evaluation | 0.1 | `7adad2d...` |
| Operational telemetry | TESTED | `devintel/operations/telemetry.py`; bounded/autonomy stores | telemetry/bounded/runtime/autonomy tests | successful CI | bounded execution, SQLite | evidence only | richer provider/resource metrics pending | Feed verified outcomes into runtime learning | 0.2 | `d73d6b6...` |
| Full autonomous operating path | VERIFIED | `devintel/autonomy/`, executive, operations, capabilities, routing, learning | autonomy/safety/cycle/runtime/routing/learning tests | earlier milestones passed CI; latest learning-routing merge not exposed | cognition, routing, resource/capability, permission, verification | bounded, permission-preflighted, finite, proposal-only improvement | semantic goal understanding still bounded; latest CI evidence pending | Complete semantic goal understanding | 0.7 | `ec62eae...` |
| Production capability source configuration | IMPLEMENTED | `devintel/capabilities/sources.py` | `tests/test_capability_sources.py` | latest source post-fix CI not exposed | explicit source config, trusted evidence policy, HTTPS scout | disabled by default; host/timeout/size/trust gates | no source is silently trusted or installed | Operationally validate legitimate configured sources | 1.0 | `5a1dde...` |
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
| Self-Model / Resilience / Continuous Evolution | PARTIAL | autonomy, monitoring, security, recovery, capability lifecycle | autonomy/security/monitoring tests | successful CI | observations, metrics, recovery, controlled improvement | proposal-only improvement | no general semantic autonomy | Integrate semantic understanding and richer resilience | 0.3 | `ec62eae...` |

## Highest-priority gaps

1. **General semantic natural-language goal understanding** — the safety boundary exists, but the deterministic interpreter is intentionally not a general semantic model.
2. **Broad ecosystem capabilities** — communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
3. **Distributed resource/provider scheduling** — current routing is deterministic/local.
4. **Production operational evidence** — the available GitHub integration has not exposed workflow/status checks for the latest merged learning/routing commit.

## Blocked vs not built

Missing credentials or platform verification are not software failures. They become `BLOCKED` only when software is ready and an external owner/platform action is genuinely required.

At this checkpoint no listed major capability is `BLOCKED`; several remain not built.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
