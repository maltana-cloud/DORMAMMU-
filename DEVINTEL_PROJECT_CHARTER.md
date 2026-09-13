# DORMAMMU PROJECT CHARTER

## 1. What DORMAMMU Is

DORMAMMU is a **general-purpose autonomous intelligence and ecosystem platform**.

It is not merely a news bot, Telegram bot, developer bot, scraper, chatbot, or publishing scheduler. Those are possible interfaces or capabilities built on top of the intelligence engine.

DORMAMMU's long-term purpose is to continuously:

**OBSERVE → DISCOVER → UNDERSTAND → VERIFY → IDENTIFY DEMAND → CREATE → DISTRIBUTE → CREATE AWARENESS → MONETIZE → MEASURE → EVOLVE**

while preserving truth, safety, owner control, modularity, and graceful degradation.

## 2. What It Is Being Built To Do

DORMAMMU should eventually be able to:

- discover useful information across many domains;
- understand and organize that information;
- verify important claims and preserve provenance;
- detect contradictions, uncertainty, freshness, and duplicates;
- maintain knowledge and context;
- converse naturally with users and communities;
- publish useful information when there is genuine value, rather than blindly following schedules;
- participate in authorized groups, channels, discussions, and communities where platform rules and permissions allow;
- discover unmet needs and opportunities;
- create or improve useful tools and services;
- test and deploy tools through controlled execution environments;
- distribute useful products, information, and services through appropriate channels;
- measure outcomes and system health;
- identify legitimate revenue opportunities;
- track revenue and costs;
- recommend where revenue should be reinvested based on bottlenecks and expected value;
- discover new domains, markets, technologies, communities, and opportunities for expansion;
- report important operational, security, financial, and strategic state to its authorized owner.

## 3. Domain Scope

The first domain is developer/technology intelligence, but the architecture MUST remain domain-independent.

Future domains may include, for example:

- AI
- software development
- cybersecurity
- football and sports
- crypto and markets
- jobs and careers
- startups and business
- world news
- gaming
- education
- research
- products and services
- emerging technologies
- other useful domains discovered through the system's own research

A domain is a configuration and capability composition, not a reason to duplicate the entire engine.

## 4. Natural Intelligence and Publishing

DORMAMMU must not behave like a blind scheduled poster.

The intended behavior is:

- Nothing important → stay quiet.
- Important development → investigate → verify → speak.
- Developing story → update naturally when new verified value appears.
- User asks a question → respond naturally.
- Related developments → combine them into useful context rather than spam.
- Opportunity → investigate legitimacy and relevance before presenting it.
- No meaningful value → do not publish.

Different channels may have different audiences, permissions, memory, sources, tone, and natural rhythms without corrupting one another.

## 5. Multi-Channel and Community Architecture

The same intelligence engine should be able to serve many independent channels and communities.

Each channel/community must have isolated configuration and operational state, including where applicable:

- audience
- domain/topic scope
- sources
- memory/context
- permissions
- tone and presentation
- content policy
- publishing policy
- opportunity policy
- destination
- analytics
- health/status

A failure or compromise in one channel must not automatically compromise the core, owner controls, other channels, or unrelated revenue state.

Community participation must respect platform rules, permissions, rate limits, anti-spam requirements, and human/community boundaries. DORMAMMU must not use fake engagement, vote manipulation, deceptive identity, or spam.

## 6. Opportunity Creation and Business

DORMAMMU is intended to **manufacture usefulness, not engagement**.

It should not merely report opportunities. When it identifies a genuine unmet need, it may eventually:

1. understand the need;
2. check whether a solution already exists;
3. design a solution;
4. build or integrate a tool;
5. test it safely;
6. distribute it where appropriate;
7. create legitimate awareness;
8. monetize it when appropriate;
9. measure results;
10. improve or retire it.

Money must never override truth. Sponsored, affiliate, or commercial recommendations must remain relevant and appropriately disclosed. The highest-paying option must not automatically become the recommended option.

DORMAMMU starts with a **₦0 budget**. Revenue may later be reinvested into infrastructure, providers, tools, distribution, and other bottlenecks with owner-controlled financial boundaries.

## 7. Autonomous Action Boundary

Intelligence and authority are separate.

DORMAMMU may automatically perform routine, low-risk, approved work. Safeguarded work requires stronger checks. Spending money, sensitive account connections, major architecture changes, commercial agreements, and high-risk or irreversible actions require owner approval unless a separately approved policy explicitly says otherwise.

DORMAMMU must never acquire unrestricted authority merely because it can technically execute an action.

## 8. Security Philosophy

Security is based on the principle that unknown attacks may succeed, so the system must be designed for:

**DETECT → CONTAIN → ISOLATE → UNDERSTAND → RECOVER → VERIFY → LEARN**

Security must be observable to the authorized owner but inconspicuous to everyone else.

External web pages, feeds, messages, documents, community posts, and generated content are untrusted data. They are never automatically system instructions, permissions, or authority.

Foundational security, owner-control, trust, and recovery boundaries must not be silently rewritten by an autonomous component.

## 9. Modularity and Continuity

Every major capability must have a clear responsibility and stable boundary.

Providers, platforms, AI models, databases, and external services should be replaceable wherever practical.

A failure in one subsystem should degrade that subsystem rather than destroy unrelated capabilities.

Git history, tests, `DEVINTEL_STATUS.md`, and this charter together provide continuity between human and AI contributors. The legacy status filename is retained for compatibility; the canonical product identity is DORMAMMU.

## 10. Current Build Order

The project is developed in major systems. The active system must be completed and verified before moving to the next major system unless the owner explicitly changes scope.

### System 1 — Core Intelligence

Orchestration, event flow, task execution, planning, decision-making, runtime state, permission hooks, auditability, error handling, recovery hooks, configuration, and tests.

### System 2 — Knowledge & Research

Discovery, source providers, ingestion, normalization, deduplication, storage, extraction, structured knowledge, provenance, verification hooks, opportunity discovery, scoring, routing, and tests.

### System 3 — Truth & Security

Verification, contradiction detection, provenance/trust, threat detection, permission enforcement, isolation, containment, recovery, and security observability.

### System 4 — Conversation & Memory

Natural conversation, context, long-term memory, community conversation state, owner communication, and safe memory boundaries.

### System 5 — Distribution & Community

Telegram and other platforms, channels, groups, comments/discussions, community participation, natural publishing, routing, and per-community isolation.

### System 6 — Tool Builder

Problem detection, solution discovery, tool generation/integration, sandbox testing, deployment, monitoring, repair, and controlled updates.

### System 7 — Growth & Awareness

Audience discovery, useful awareness, distribution intelligence, partnerships, and growth measurement.

### System 8 — Opportunity & Business

Opportunity discovery, products/services, legitimate monetization, affiliate/sponsor safety, revenue tracking, and commercial boundaries.

### System 9 — Reinvestment & Strategy

Cost/revenue analysis, bottleneck detection, resource allocation recommendations, domain evaluation, expansion, and retirement decisions.

### System 10 — Monitoring & Owner Control

Health, queues, channel state, security state, finances, strategic reporting, approvals, emergency controls, and owner-facing control center.

## 11. Rules for Every AI Contributor

Before doing any work, every AI MUST understand:

1. **What DORMAMMU is:** a broad autonomous intelligence and ecosystem platform.
2. **What DORMAMMU is not:** a single-purpose news bot or a collection of unrelated scripts.
3. **The complete mission:** the capabilities described in this charter.
4. **The current milestone:** read `DEVINTEL_STATUS.md`.
5. **The architecture:** inspect the relevant code, tests, and recent commits.
6. **The boundaries:** read `AI_WORKING_RULES.md` and preserve its safety, security, free-first, and scope rules.
7. **The next task:** continue the active milestone rather than inventing a different project.

An AI must not start coding from a narrow interpretation of the last user sentence while ignoring this charter.

## 12. Completion Standard

A subsystem is not considered complete because files exist or a happy-path demo works.

Completion requires:

- implementation matches the charter and architecture;
- public contracts are stable and documented;
- normal behavior works;
- invalid input is handled;
- failures are contained appropriately;
- security/permission boundaries are preserved;
- provenance and uncertainty are represented where relevant;
- relevant tests pass;
- no accidental unrelated changes remain;
- the status checkpoint is updated;
- the next AI can resume without the previous conversation.

## Final Principle

**DORMAMMU exists to continuously turn verified understanding into useful action and sustainable value — without sacrificing truth, safety, owner control, or the ability to evolve.**
