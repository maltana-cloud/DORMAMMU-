# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Current checkpoint:** Categories 1–27 are complete and locked at their defined repository boundaries. Ω.1 bounded distributed mission coordination is complete and locked. The new human ecosystem/distribution/media surface is recorded as a requirement/design and is not claimed implemented. Production readiness remains unclaimed.

| Category | Capability | Status | Repository boundary / evidence | Key limitation |
|---|---|---|---|---|
| 1 | Foundation & Governance | COMPLETE / LOCKED | Charter, rules, state, governance controls | Real deployment governance evidence remains future work |
| 2 | Core Intelligence | COMPLETE / LOCKED | Cognition, evidence synthesis, routing, learning, bounded self-model | Provider-specific operational evidence remains future work |
| 3 | Capability & Resource Intelligence | COMPLETE / LOCKED | Discovery, provenance, lifecycle, inventory, resource control | Distributed/provider-backed scheduling remains future work |
| 4 | Ecosystem Awareness | COMPLETE / LOCKED | Bounded aggregation and approved awareness adapter | Live global polling/distribution remains future work |
| 5 | Engineering Intelligence | COMPLETE / LOCKED | Bounded repository/code intelligence and safety tests | Full vulnerability/repair loop remains future work |
| 6 | Language & Communication | COMPLETE / LOCKED | Language normalization, tokenization, intent/risk hints, response constraints | Production speech/provider adapters remain future work |
| 7 | Research & Domain Expansion | COMPLETE / LOCKED | Domain evidence/proposal/assessment/registry contracts | No unrestricted crawling, installation, authentication, spending, or execution |
| 8 | Creative Intelligence | COMPLETE / LOCKED | Ideation, variation, planning, critique/repair, consistency, provider fallback, lineage | Real provider credentials/quotas remain environment-dependent |
| 9 | Simulation & Interactive Worlds | COMPLETE / LOCKED | Deterministic worlds/actions/ticks, replay integrity, persistence/recovery | No production physics/rendering/multiplayer authority |
| 10 | Social & Community Intelligence | COMPLETE / LOCKED | Community observation, demand/question/opportunity/risk signals, response planning, provenance | Real platform adapters and live distribution remain future work |
| 11 | Economic & Business Intelligence | COMPLETE / LOCKED | Opportunity/evidence analysis, business planning/comparison, advisory persistence | No unrestricted financial authority |
| 12 | Owner & Platform Security | COMPLETE / LOCKED | Authenticated owner approvals, containment/recovery, audit chain, security regression coverage | Production identity/session and deployment security remain external work |
| 13 | Autonomous Operations | COMPLETE / LOCKED | Bounded observe/plan/permission/act/verify/record/improve cycles and supervisor | Production distributed workers/schedulers remain future work |
| 14 | Evolution & Self-Improvement | COMPLETE / LOCKED | Evidence-gated candidates, independent evaluation, versioned promotion, rollback, durable records | Production experimentation/training remains future work |
| 15 | Production Runtime & Orchestration | COMPLETE / LOCKED | Runtime composition, bounded orchestration and lifecycle/resource integration | Production deployment evidence remains future work |
| 16 | Persistent Intelligence Infrastructure | COMPLETE / LOCKED | Durable knowledge, operational, autonomy and lifecycle stores | Production HA/distributed persistence remains future work |
| 17 | Real Capability & Provider Infrastructure | COMPLETE / LOCKED | Provider contracts, routing, live adapters, health/fallback boundaries | External credentials/quotas remain environment-dependent |
| 18 | Intelligence & Knowledge System | COMPLETE / LOCKED | Knowledge ingestion/synthesis with provenance, contradictions and uncertainty | Global source coverage remains future work |
| 19 | Research & Discovery Engine | COMPLETE / LOCKED | Bounded research/discovery and verification flow | No unrestricted crawler or automatic truth admission |
| 20 | Problem & Opportunity Discovery | COMPLETE / LOCKED | Demand/problem/opportunity identification behind evidence boundaries | Real-world market validation remains future work |
| 21 | Domain Intelligence | COMPLETE / LOCKED | Domain modeling and verified domain signals | Broad domain coverage remains extensible work |
| 22 | Human–DORMAMMU Collaboration | COMPLETE / LOCKED | Scoped collaboration, owner control and safe human interaction boundaries | Production multi-channel integration remains future work |
| 23 | Long-Running Mission System | COMPLETE / LOCKED | Bounded mission lifecycle, persistence, recovery, and Ω.1 atomic worker coordination | Production distributed scheduling remains future work |
| 24 | Ecosystem & Multi-Agent Coordination | COMPLETE / LOCKED | Scoped agent coordination, contracts and failure boundaries | Heterogeneous production agent fleet remains future work |
| 25 | Real-World Action Infrastructure | COMPLETE / LOCKED | Provider-independent action contracts, permission-gated execution, deterministic fallback, dry-run, idempotency, verification and audit | No platform credentials/OAuth, distributed exactly-once side effects, rollback of external transactions, or unrestricted financial authority |
| 26 | Global Intelligence & Continuous Discovery | COMPLETE / LOCKED | Bounded multi-source discovery rounds, health/failure isolation, scope/freshness gates, deterministic deduplication and scheduling boundary | No unrestricted polling, global coverage, source reputation engine, or automatic truth admission |
| 27 | DORMAMMU Ecosystem Evolution | COMPLETE / LOCKED | Bounded orchestration of verified learning proposals into evaluated, reversible ecosystem changes with capability-health gating and rollback | No self-authorized code/security/authority changes, automatic installation, spending, publication, or unrestricted self-modification |
| Ω.1 | Bounded Distributed Mission Coordination | COMPLETE / LOCKED | Atomic SQLite worker leases, expiry takeover, renewal, ownership-checked checkpoint/failure completion | Not production-grade multi-host scheduling; requires operational deployment evidence |
| Ω.H | Human Ecosystem, Distribution & Media | REQUIREMENT / DESIGNED | `DORMAMMU_HUMAN_ECOSYSTEM_DISTRIBUTION_MEDIA.md` and `DORMAMMU_HUMAN_ECOSYSTEM_REQUIREMENTS.md` define natural chat, tenant-isolated connections, cross-domain channel/social distribution, legitimate self/product promotion, user channel management, economic separation, and video/audio/image/PDF workflows | No live social/channel integrations, production media workers, credential vault implementation for this surface, or production distribution/monetization evidence yet |

## Ω.H design boundary

The human ecosystem surface is additive. It does not reopen locked foundations or create a new authority system.

Natural chat is a communication layer; personality does not grant authority. External accounts are tenant-scoped capabilities. User and owner connections must be isolated, and raw credentials must remain inside protected secret boundaries. Distribution is provider-adapter based and can span social networks, messaging channels, communities, websites, publications, marketplaces, and future surfaces. Growth must remain genuine and non-deceptive.

Media/document workflows cover authorized acquisition, inspection, extraction/understanding, transformation/editing, verification/quality, packaging, and distribution for video, audio, images, PDFs, and future formats. Acquisition must respect access controls, licensing, copyright, DRM, privacy, and provider rules.

User earnings and DORMAMMU revenue remain separate accounting scopes. Payment, identity verification, CAPTCHA/OTP, provider security controls, and other consequential authorization boundaries are never bypassed.

## Ω.1 completion boundary

Ω.1 extends the existing durable mission system with a coordination boundary for multiple workers/processes. A worker can atomically claim a due mission with a finite lease, renew it, and complete/fail only while it owns the active lease. An expired lease can be taken over. Existing mission databases are migrated additively without resetting mission data.

Leases are coordination only. They do not install capabilities, authenticate providers, grant permissions, alter protected security/owner/recovery/code surfaces, spend money, publish externally, or execute arbitrary external actions.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
