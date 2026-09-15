# DORMAMMU — UNKNOWN FRONTIER & UNIVERSAL INTELLIGENCE ROADMAP

> Canonical architectural roadmap for capabilities discussed after the Ω.3 checkpoint. This document defines future capability intent and engineering boundaries. It does **not** claim these capabilities are implemented merely because they are documented.

## Purpose

DORMAMMU's long-term direction is to continuously expand the boundary between what is known and what is unknown, turning verified understanding into useful action and sustainable value. The objective is not omniscience. The objective is an intelligence that can acquire knowledge, model the world, reason across domains, recognize uncertainty and knowledge gaps, investigate what can be investigated, discover new knowledge, learn from outcomes, and act autonomously within explicit authority and safety boundaries.

## Capability stack

The following capabilities are architectural targets and must be implemented incrementally through the repository's existing contracts and locked foundation:

1. **Universal knowledge acquisition** — acquire knowledge across accessible domains and sources rather than depending on a fixed knowledge corpus.
2. **World knowledge** — represent facts, entities, concepts, events, processes, and relationships across domains.
3. **Knowledge graph / knowledge fabric** — preserve relationships, provenance, confidence, timestamps, contradictions, revisions, and scope.
4. **World modeling** — represent states, dependencies, causal hypotheses, processes, dynamics, and possible outcomes where evidence permits.
5. **Context awareness** — determine what information and state are relevant to the current objective, mission, environment, and user intent.
6. **Intent understanding** — map requests and observations to explicit goals, requirements, constraints, and expected outcomes.
7. **Reasoning** — derive conclusions from evidence and models while distinguishing inference from established fact.
8. **Planning and decision intelligence** — select and adapt sequences of actions toward objectives under resource, permission, uncertainty, and risk constraints.
9. **Learning and meta-learning** — learn from verified outcomes and improve methods for acquiring and using knowledge.
10. **Epistemic intelligence** — represent what DORMAMMU knows, does not know, believes, why it believes it, confidence, evidence quality, and what evidence could change the conclusion.
11. **Active information seeking** — identify missing information and determine whether additional evidence can be obtained, then pursue authorized evidence acquisition.
12. **Scientific / technical discovery** — formulate hypotheses, compare explanations, run permitted computation or experiments, evaluate results, and record reproducible evidence.
13. **Simulation and forecasting** — explore possible futures and consequences without treating predictions as certainty.
14. **Contradiction and uncertainty management** — preserve unresolved disagreement and uncertainty rather than silently choosing an answer.
15. **Problem and opportunity discovery** — identify significant unmet needs, anomalies, bottlenecks, opportunities, and research gaps from verified signals.
16. **Autonomous execution** — continuously perform bounded work through observe → understand → plan → permission → security → act → verify → record → improve loops.
17. **Persistent autonomous missions** — continue multi-step objectives across restarts and worker handoffs using durable state and bounded coordination.
18. **Specialist/model/provider orchestration** — select appropriate models, agents, tools, providers, and compute resources while keeping them replaceable and non-authoritative.
19. **Controlled self-improvement** — diagnose capability gaps, propose improvements, test them in isolation, independently evaluate them, and promote only verified reversible changes within policy.
20. **Metacognition** — monitor capability limits, reasoning quality, uncertainty, failures, resource use, and knowledge gaps; never convert self-assessment into authority.
21. **Ecosystem creation and value realization** — eventually connect discovery and solution creation to authorized creation, distribution, awareness, measurement, and monetization pathways.

## The knowledge-boundary problem

DORMAMMU must explicitly distinguish at least:

- **KNOWN** — supported by appropriate evidence within the relevant scope.
- **PROBABLE** — supported inference with meaningful uncertainty.
- **UNCERTAIN** — evidence is insufficient for a strong conclusion.
- **CONTRADICTORY** — credible evidence conflicts and remains unresolved.
- **INCOMPLETE** — important information is missing.
- **UNKNOWN-BUT-INVESTIGABLE** — currently unknown but additional authorized evidence may reduce the gap.
- **CURRENTLY-INACCESSIBLE** — the required information cannot currently be obtained through available authorized channels.
- **POTENTIALLY-UNDECIDABLE** — a formal question may be undecidable within the specified formal system; this is a mathematical property to investigate, not a generic excuse for failure.

These states are epistemic states, not permissions. An unknown does not justify hallucination, and an investigable unknown does not grant access to external systems.

## How DORMAMMU should attack the boundary

### 1. Never observed
`UNKNOWN → IDENTIFY OBSERVABLES → ACQUIRE AUTHORIZED EVIDENCE → TEST → VERIFY → UPDATE KNOWLEDGE`

### 2. Insufficient evidence
`UNCERTAIN → IDENTIFY MISSING EVIDENCE → VALUE OF INFORMATION → ACQUIRE IF AUTHORIZED → REASSESS`

### 3. Future uncertainty
`CURRENT STATE → MODEL → HYPOTHESES → SCENARIOS → PROBABILISTIC FORECAST → OBSERVE → UPDATE`

Predictions remain predictions; observed outcomes update the model.

### 4. Measurement uncertainty
`MEASURE → CALIBRATE → QUANTIFY ERROR → REPEAT/CROSS-CHECK → INFER → RECORD CONFIDENCE`

### 5. Contradictory knowledge
`CONFLICT → PRESERVE SOURCES → ASSESS PROVENANCE → TEST COMPETING CLAIMS → RESOLVE OR RETAIN CONFLICT`

Popularity, recency, or model preference must not silently replace evidence.

### 6. Incomplete knowledge
`GAP DETECTION → PRIORITIZE → SEARCH/RESEARCH/EXPERIMENT → VERIFY → FILL GAP OR RECORD LIMITATION`

### 7. Mathematical limits
`QUESTION → FORMALIZE → CHECK KNOWN RESULTS/DECIDABILITY → ATTEMPT PROOF/COUNTEREXAMPLE → DETERMINE LIMIT → REPORT PRECISELY`

A stronger formal framework may permit questions that are not decidable in a weaker one, but changing a framework does not erase the original theorem or limitation.

### 8. No possible access path
`INACCESSIBLE → IDENTIFY ACCESS BOUNDARY → DO NOT INVENT → MONITOR FOR NEW AUTHORIZED EVIDENCE`

Intelligence must include the ability to say **"not knowable from the information currently available"** and explain what would be required to know more.

## Universal intelligence operating loop

The long-term target is:

`PERCEIVE → UNDERSTAND → MODEL → IDENTIFY GAPS/PROBLEMS → RESEARCH → HYPOTHESIZE → PLAN → PERMISSION CHECK → SECURITY CHECK → EXPERIMENT/SIMULATE/ACT → OBSERVE → VERIFY → LEARN → UPDATE KNOWLEDGE/MODEL → REFLECT → SELECT NEXT OBJECTIVE → CONTINUE`

This is an architectural target, not a claim that every stage is currently implemented at production quality.

## Autonomy levels

DORMAMMU should be able to progress through explicit bounded levels rather than jumping directly to unrestricted autonomy:

- **Reactive:** responds to owner requests.
- **Assisted:** executes an owner-defined objective through bounded plans.
- **Proactive:** identifies useful problems, gaps, or opportunities and proposes work.
- **Bounded autonomous:** independently researches, tests, builds, and evaluates authorized work.
- **Persistent autonomous:** maintains long-running objectives, state, observation, learning, and next-step selection within policy.
- **Open-ended discovery:** investigates novel questions and expands knowledge through authorized research and experimentation.

Autonomy never overrides owner authority, security, truth, resource limits, external platform rules, or irreversible-action controls.

## Resource and cost strategy

The initial implementation should maximize zero-cost and existing resources:

`EXISTING → REUSE → TRUSTED OPEN SOURCE → FREE PROVIDER → LOCAL COMPUTE → BUILD/FINE-TUNE → LOW-COST PAID → EXPENSIVE`

The architecture must remain provider/model/compute agnostic so that constrained local or free resources can be used now and stronger resources can be plugged in later without rewriting the protected foundation.

Free availability is a resource constraint, not a reason to weaken truth, security, licensing, quota, identity, or permission controls.

## What this roadmap does not authorize

This roadmap does not authorize:

- unrestricted self-modification;
- bypassing CAPTCHAs, quotas, licensing, authentication, OAuth, payments, exchange controls, or platform security;
- automatic spending or financial authority;
- access to private data or systems without authorization;
- publication, communication, deployment, or account actions without live permission;
- treating model output as truth;
- treating historical memory as current authority;
- claiming production readiness without operational evidence.

## Implementation rule

No future builder should implement this roadmap by replacing the current foundation. The repository's existing charter, security, owner authority, truth, recovery, compatibility, and locked milestones remain authoritative. New capability work must be additive and follow:

`RECONSTRUCT → INSPECT → IDENTIFY GAP → DEFINE CONTRACT → ISOLATE → PERMISSION → SECURITY CHECK → IMPLEMENT → TEST → INTEGRATE → VERIFY → DOCUMENT → COMMIT → CI → CHECKPOINT → CONTINUE`

When a capability is documented here but not proven in code and tests, its status remains **PLANNED/DESIGNED**, not implemented.

## Starting rule for future builders

Do not start by building every capability listed above. First inspect the actual repository and current Ω checkpoint, then choose the highest-leverage **repository-solvable dependency gap** that advances the operating loop without reopening locked foundations.

**North Star:** DORMAMMU does not need to claim omniscience. It needs the architecture to continuously expand what it can know, understand, test, discover, create, and safely act upon — while knowing the difference between knowledge and ignorance.
