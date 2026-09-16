# DORMAMMU Human Ecosystem Requirements

## Status

`REQUIREMENT / ARCHITECTURAL DESIGN` — not an implementation claim.

This requirement extends the existing DORMAMMU economic, human-collaboration, identity/account, provider, research, and creative architecture.

## Natural chat

DORMAMMU should provide a direct natural-language interaction surface where users can converse with it as an intelligence rather than issuing rigid commands. Communication may adapt to context and user preference: conversational, serious, concise, energetic, humorous, light sarcasm, educational, professional, or other appropriate styles.

Personality is a communication policy only. It must never alter authorization, permissions, credential access, financial authority, safety controls, or audit requirements.

## User-owned social/channel connections

Provide a dedicated connection center where each user can link authorized social accounts, channels, communities, communication services, and other external identities without exposing other users' or owner accounts.

Required isolation:

`TENANT → USER IDENTITY → CONNECTION → SCOPED CAPABILITY → AUTHORIZED ACTION`

Raw credentials belong in the protected credential boundary. Agents should receive scoped connection/capability references rather than global credentials. Owner and user connections must be cryptographically/architecturally separated by scope. Cross-user access must fail closed.

Use legitimate provider authorization, such as OAuth where available. Do not bypass CAPTCHA, OTP, identity verification, consent, payment authorization, platform security, quotas, DRM, licensing, or access controls.

## Cross-domain presence and distribution

DORMAMMU should be able to discover and operate appropriate distribution surfaces across domains, including social networks, messaging channels, communities, websites, publications, newsletters, marketplaces, media platforms, educational channels, professional networks, and future providers.

Platform-specific integrations should be adapters behind a common contract so a new provider does not require redesigning the intelligence layer.

Distribution loop:

`DOMAIN → AUDIENCE → NEED → OPPORTUNITY → CHANNEL → AUTHORIZED PRESENCE → CONTENT/SERVICE → CONVERSATION → OUTCOME → MEASURE → LEARN`

DORMAMMU may promote its own products/services and authorized user products/services when relevant, but distribution must remain useful, truthful, non-deceptive, non-spammy, and compliant with provider rules.

## Channel/social management

Users should be able to choose an autonomy mode for connected channels:

- Assist: drafts and recommendations.
- Co-pilot: routine authorized actions with approval for sensitive actions.
- Managed: continuous operation within an explicit policy.
- Autonomous: bounded continuous operation with explicit scopes, policies, resource limits, audit, verification, and recovery.

Potential operations include content planning, drafting, scheduling, publishing, permitted replies, moderation, analytics, audience research, opportunity discovery, and campaign measurement.

## Economic participation

DORMAMMU should support legitimate opportunities generated through its ecosystem. A user may use DORMAMMU to discover or perform work, manage a channel/business, sell services/products, or participate in authorized opportunities. DORMAMMU may have separate revenue streams such as subscriptions, marketplace/service fees, products, or other legitimate commercial models.

User earnings and DORMAMMU revenue must remain separate accounting scopes. No hidden deduction or ownership transfer occurs merely because DORMAMMU manages a channel or helps create an opportunity.

## Media/document intelligence

Provide a common media/document fabric covering video, audio, images/photos, PDFs, and future formats discovered through capability discovery.

Pipeline:

`ACQUIRE → INSPECT → EXTRACT/UNDERSTAND → TRANSFORM/EDIT → VERIFY/QUALITY → PACKAGE → DISTRIBUTE`

Potential video operations: metadata inspection, transcription, trimming, cutting, merging, resizing, aspect-ratio conversion, captions/subtitles, clip extraction, short-form variants, voice-over, permitted audio changes, thumbnails, format conversion, and quality checks.

Potential audio operations: transcription, noise cleanup, trimming, merging, normalization, format conversion, voice-over, synchronization, and podcast/clip preparation.

Potential image operations: OCR, resizing, cropping, conversion, thumbnails, enhancement, authorized background operations, object/text extraction, and platform-specific preparation.

Potential PDF/document operations: authorized acquisition, parsing, OCR, extraction, summarization, comparison, evidence extraction, report generation, conversion, and publication preparation.

Content acquisition and transformation must respect ownership, privacy, licensing, copyright, DRM, platform terms, and access controls. Public availability does not automatically grant every downstream use right.

## Knowledge-to-media-to-market loop

DORMAMMU should eventually be able to transform verified knowledge into multiple useful outputs and distribute them through authorized channels:

`RESEARCH → EVIDENCE → VERIFICATION → SYNTHESIS → SCRIPT/PLAN → MEDIA/DOCUMENT → QUALITY CHECK → PLATFORM VARIANTS → AUTHORIZED DISTRIBUTION → MEASUREMENT → LEARNING`

One source may legitimately produce an article, report/PDF, infographic, video, short-form clip, podcast segment, newsletter, or community post when rights and permissions permit.

## Required integration boundaries

These capabilities must reuse the existing DORMAMMU boundaries for identity, authentication, sessions, capabilities, authority, resource reservations, provider health/fallback, verification, owner control, telemetry, audit, recovery, and learning.

No new interface, social connector, media processor, or growth engine may create a parallel authority path.

Implementation status must progress through the repository truth ladder:

`REQUIREMENT → ARCHITECTURAL DESIGN → IMPLEMENTED → TESTED → PRODUCTION VERIFIED`
