---
status: DRAFT
---

# Product

Replace bracketed placeholders. Remove sections that do not apply. Keep this document at **product intent**; put architecture, repo layout, and stack in `STRUCTURE.md` and `TECH.md`.

## Summary

[One paragraph: what this is, for whom, primary geography or segment if relevant, and what MVP explicitly targets vs defers.]

**Working product name:** [name]. **Repository / codename (if different):** [folder or internal name]. Align final branding when ready. If the working name could be confused with another product or tool, note that here.

## Vision

[2–4 sentences: the long-term direction—what “winning” looks like without listing every feature.]

## Problem Statement

- [Pain 1 — concrete, observable.]
- [Pain 2.]
- [Pain 3.]

[Closing sentence tying pains to why this product should exist.]

## Target Users

### Primary User

[Who they are, context, constraints.]

### Secondary User

[Optional — who comes next, not MVP focus if so stated.]

### Initial Market

[Geography, segment, or go-to-market boundary for MVP.]

## MVP Goal

[Single cohesive paragraph: end-to-end outcome a user can achieve in MVP. List 3–7 bullet capabilities if helpful. State experience bar: simple, fast, mobile-friendly, production-oriented — adjust as needed.]

## Core Value Proposition

**Primary message:** [one line].

**Supporting reasons:** [save time, reduce risk, consolidate tools — what you actually deliver emotionally and practically.]

**Differentiator for MVP:** [one sharp claim you can test, e.g. time-to-value or a measurable user outcome.]

## MVP Scope

Organize by domain or theme. Keep bullets testable.

### [Area 1 — e.g. Authentication and Profile]

[Capabilities, roles, tenancy rules for MVP.]

### [Area 2 — e.g. Core Domain]

[Entities, main actions, status models if any.]

### [Area 3]

[…]

### Dashboard / Overview (if applicable)

[What “operational” visibility means in MVP — not full BI unless in scope.]

## Out of Scope

[Explicit list for this phase or forever-out items. Reduces scope creep and clarifies roadmap boundaries.]

## User Journey

1. [Step — user perspective, outcome-oriented.]
2. […]
3. […]
4. […]
5. […]

## Functional Requirements

State **acceptance-oriented** requirements that QA can verify. Avoid duplicating **MVP Scope** verbatim—reference domains above and spell out **must** behaviors and constraints. Omit this section if **MVP Scope** is already written as checklist-level, testable bullets.

### [Requirement group 1]

- [ ] [Testable requirement.]
- [ ] […]

### [Requirement group 2]

- [ ] […]

## Degradation and Failure (product-level)

How the product should behave when things go wrong—without prescribing implementation.

- **[Dependency or failure mode]:** [e.g. external API down → user can still … / clear retry / no silent data loss.]
- **[Another case]:** […]
- **Data integrity:** [e.g. nothing committed as final record of record without explicit user confirmation, if that applies.]

## AI / Automation (if applicable)

### Inputs

[What the system may use — user content, context, metadata.]

### Outputs

[What is produced — drafts, summaries, structured fields.]

### Rules

[Framing: assistive vs authoritative; disallowed claims; regional or professional constraints.]

### Human-in-the-Loop

[Review, edit, approve before persistence or external effect — as applicable.]

## Security and Privacy Requirements

[PHI, PII, and sensitive health-adjacent data; access control model for MVP; encryption expectations; auditability; retention — at product policy level. Point to `TECH.md` and legal review for implementation detail.]

## Product Principles

- [Principle 1 — e.g. speed over breadth for MVP.]
- [Principle 2.]
- [Principle 3.]

## Data Model Overview

[High-level entities and relationships only. Refine in design docs and implementation.]

- **[Entity]:** [one line.]
- **[Entity]:** […]

## Success Metrics

[North star or primary outcome if known.] Examples to validate with stakeholders:

- [Metric 1 — definition + why it matters.]
- [Metric 2.]
- [Qualitative signal, e.g. interviews or surveys.]

## Risks

### Product Risks

[Adoption, trust, scope creep.]

### Technical Risks

[Latency, accuracy, integration, scale.]

### Market Risks

[Competitors, substitutes, buying behavior.]

## Future Roadmap Ideas

[Ordered or unordered list — not commitments.]

## Positioning

[One short paragraph for pitch, landing copy, or internal alignment.]

## MVP Release Standard

Pilot- or launch-ready when:

- [Criterion 1 — end-to-end journey.]
- [Criterion 2 — performance / reliability bar.]
- [Criterion 3 — safety, privacy, or compliance bar.]
- [Criterion 4 — no critical misrepresentation of automated or AI output, if applicable.]

## Implementation Guidance

[Priorities for engineering and design: what to optimize first; dependency on `STRUCTURE.md` / `TECH.md`; preference for explicit contracts and user-visible disclaimers where relevant. Detailed performance targets, SLOs, and infra-level constraints belong in `TECH.md`.]

## Open Questions

| # | Question | Owner | Target date |
|---|----------|-------|-------------|
| 1 | […] | […] | […] |
| 2 | […] | […] | […] |

## Related Documents

- `README.md` — overview, quickstart, and links to root docs and `spec/`.
- `STRUCTURE.md` — [repo and module layout when it exists.]
- `TECH.md` — [stack, ADRs, and non-functional / operational constraints when it exists.]
- `spec/<spec_name>/` — [per-feature **`DESIGN.md` → `REQUIREMENTS.md` (EARS) → `tasks/N_*.plan.md`** when used; see `spec/README.md`; Cursor: `@spec`]
