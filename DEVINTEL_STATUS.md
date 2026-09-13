# DORMAMMU STATUS

## Current Milestone
**Live Provider Layer — controlled external research and optional model adapters**

## Completed
- [x] Systems #1–#10 foundations merged
- [x] Plugin / Specialist Engine Framework merged
- [x] Runtime composition, Owner Control, and Provider boundaries merged
- [x] Research, Conversation, Opportunity, Truth, Community, Growth, Business, Strategy, Tool Builder, Monitoring specialists merged
- [x] Bounded autonomous operating loop merged
- [x] Education foundation and Education Specialist merged
- [x] Research + Truth education adapters merged
- [x] Cross-subsystem Education signal adapters merged in PR #31
- [x] Adaptive curriculum hardening merged in PR #32
- [x] Channel-specific TeachingProfile and TeachingEngine merged in PR #33
- [x] Assessment outcomes and OutcomeEngine merged in PR #34
- [x] Education assessment recording runs through Core Orchestrator permission checks
- [x] Scoped education outcomes are exposed as observations to the existing AutonomousEngine
- [x] Provider-neutral model generation request/response contracts merged in PR #35
- [x] Provider-neutral research retrieval contracts merged in PR #35
- [x] Bounded priority-based ProviderRouter with health checks and fallback merged in PR #35
- [x] Runtime exposes controlled generation and research routing
- [x] Provider failure/invalid-output fallback tests merged
- [x] Free, keyless Wikipedia research adapter added
- [x] Optional Gemini REST generation adapter added; credentials are environment-only
- [x] Runtime composition root auto-registers configured live providers
- [x] Adapter parsing and fail-closed configuration tests added

## Audit Note
The repository's canonical product name is **DORMAMMU**. The existing `devintel/` Python package namespace and legacy status filename are retained for backward compatibility and are not alternative product names. The earlier continuation incorrectly declared DEVINTEL canonical; that documentation error has been corrected.

## Live Provider Boundary
DORMAMMU has a provider-neutral live routing boundary:
**REQUEST → HEALTH CHECK → PRIORITY ROUTE → FALLBACK → RESULT**.

The runtime registers a free-first Wikipedia research provider automatically. A Gemini generation provider is registered only when `GEMINI_API_KEY` is explicitly configured. Both are replaceable adapters behind the same provider contracts. Provider failures and malformed output remain isolated, and the router fails closed when no usable provider exists.

Provider output is explicitly not treated as verified truth. Research/Truth remains a separate authority boundary.

## Important Qualification
The Wikipedia adapter is a **search/retrieval adapter**, not a general web research engine and not proof that an external service is always available. Its returned snippets remain evidence candidates until the Truth boundary verifies claims. The Gemini adapter is optional and is not required for the core runtime to operate.

## Authority Boundary
Education and provider routing remain capability-only. No publishing, payment, deployment, spending, moderation, security, or owner authority is created. Revenue never overrides truth or quality. Research/Truth remain authoritative for evidence and verification.

## Verification
The adapter unit tests cover JSON parsing, response validation, usage extraction, and missing-credential failure. The existing router fallback suite remains the compatibility guard. External-service availability is not represented as a passing local test; it must be observed at runtime through provider health checks.

## Next Action
Before adding another feature, audit the live adapters against the provider contracts, test the runtime wiring, and then integrate the live research path with the existing Research/Truth specialist flow. After that, connect live generation to Conversation/Education specialist decisions and complete the real autonomous operating path through the owner-authorized Distribution layer.

Telegram remains provider-controlled and owner-authorized. Live payment adapters remain later and provider-independent.

## Non-Negotiable Rule
**Every AI that works on DORMAMMU must leave a truthful, test-backed checkpoint before stopping.**
