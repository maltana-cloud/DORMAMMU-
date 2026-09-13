# DEVINTEL

**Autonomous Developer Intelligence & Community Ecosystem**

DEVINTEL is a modular, verification-first developer intelligence system designed to discover, verify, explain, publish, converse, build useful tools, and grow a trusted developer community.

## Core Principles

- **Truth before reach** — verified information outranks engagement.
- **Evidence before confidence** — facts, analysis, speculation, and uncertainty stay distinct.
- **Useful before commercial** — monetization follows genuine developer needs.
- **Autonomous, but bounded** — routine work is automated; sensitive actions require permission.
- **Modular by design** — new capabilities are added without rewriting the core.
- **Observable and reversible** — actions are recorded, health is monitored, and failures can be isolated or rolled back.
- **Free-first** — use sustainable free infrastructure and replaceable providers wherever practical.

## System Loop

`OBSERVE → UNDERSTAND → PLAN → PERMISSION CHECK → ACT → VERIFY → RECORD → IMPROVE`

## Current Runtime

DEVINTEL now has a provider-neutral live boundary:

`REQUEST → HEALTH CHECK → PRIORITY ROUTE → FALLBACK → RESULT`

The runtime can register real external adapters without coupling the core to a vendor. The current free-first research adapter uses Wikipedia's public REST API. Optional Gemini generation is enabled only when `GEMINI_API_KEY` is explicitly supplied; no credentials are stored in the repository. Provider output remains unverified until it passes the separate Truth/verification boundary.

## Architecture

```text
DEVINTEL/
├── core/
│   ├── conversation/
│   ├── memory/
│   ├── planner/
│   ├── permissions/
│   └── orchestration/
├── modules/
│   ├── research/
│   ├── verification/
│   ├── community/
│   ├── publishing/
│   ├── growth/
│   ├── monetization/
│   └── tool_builder/
├── providers/
│   ├── contracts.py
│   ├── live.py
│   ├── live_adapters.py
│   └── registry.py
├── tools/
│   ├── telegram/
│   ├── github/
│   ├── web/
│   └── registry/
├── storage/
├── config/
├── tests/
├── migrations/
└── docs/
```

## Autonomy Policy

### Automatic
- Research and discovery
- Source filtering and deduplication
- Summarization and classification
- Normal conversations
- Approved publishing workflows
- Analytics and routine health checks

### Safeguarded
- Community participation
- Small tool creation
- Routine deployments
- Provider switching within approved policy

### Owner Approval
- Spending money
- Sensitive account connections
- Major architecture changes
- Commercial agreements
- High-risk or irreversible actions

### Emergency Stop
Security incidents, suspicious behavior, repeated failures, or policy violations trigger containment and owner notification.

## Trust Model

Every important intelligence item should carry provenance and confidence information. DEVINTEL should prefer primary sources, corroborate consequential claims, detect stale information, identify duplicates, and clearly label uncertainty.

DEVINTEL must never claim to have personally tested, deployed, contacted, or observed something unless the system actually performed that action and has evidence for it.

## Status

The repository's canonical product name is **DEVINTEL**. The remaining GitHub repository slug is `DORMAMMU-` because the connected GitHub integration available to this session does not expose a repository-rename operation. No code or documentation should treat DORMAMMU as the product name.

The current milestone is the live provider layer and the next engineering target is the real autonomous operating path across Education, Conversation, Research, Truth, and Distribution.
