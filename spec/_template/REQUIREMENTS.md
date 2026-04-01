---
status: DRAFT
spec_name: "[spec-name]"
---

# Requirements: [Title]

Write behavioral requirements in **[EARS](https://alistairmavin.com/ears/)** (Easy Approach to Requirements Syntax) **where they describe system responses** to triggers, states, or optional features. Mix with narrative **Summary** / **Scope** as needed.

## EARS patterns (quick reference)

| Pattern | Form |
|--------|------|
| **Ubiquitous** | The `<system>` shall `<system response>` |
| **Event-driven** | When `<trigger>`, the `<system>` shall `<system response>` |
| **State-driven** | While `<precondition(s)>`, the `<system>` shall `<system response>` |
| **Optional** | Where `<feature is included>`, the `<system>` shall `<system response>` |
| **Unwanted behavior** | If `<trigger>`, then the `<system>` shall `<system response>` |

Use one **The … shall …** clause per requirement when possible; split if multiple independent responses.

## Summary

[One paragraph: problem, user outcome, link to `PRODUCT.md` and `DESIGN.md`.]

## Scope

- **In scope:** [bullets]
- **Out of scope:** [bullets]

## EARS requirements

### Ubiquitous

- The [system or feature name] shall [response — always true for the feature].

### Event-driven

- When [trigger / optional precondition], the [system] shall [response].

### State-driven

- While [precondition], the [system] shall [response].

### Optional (feature toggles / modules)

- Where [feature is included], the [system] shall [response].

### Unwanted behavior

- If [fault or abuse trigger], then the [system] shall [response — e.g. reject, rollback, notify].

## Non-EARS notes

[Constraints, data definitions, glossary—only if not expressible as EARS without clutter.]

## Acceptance criteria

**Spec-level** acceptance lives here in **`REQUIREMENTS.md`**: observable conditions that show each **behavioral** EARS requirement is satisfied. Prefer **one row per requirement ID** in **Traceability** (acceptance phrasing plus how it is verified—manual check, automated test name, or artifact). For a few critical flows you may add **Given / When / Then** under the same ID in **Non-EARS notes** or extra bullets—do not duplicate the EARS *shall* in different words only.

**Product-wide** or MVP checkout lists may also appear in **`PRODUCT.md`** when they span many specs; per-feature detail still maps to IDs here.

**Task-level** “done” for a slice belongs in **`tasks/N_<slug>.plan.md`** under **Definition of done**, referencing requirement IDs (e.g. `R1`) when the task only covers part of the spec.

## Traceability

| ID | EARS summary | Acceptance criteria & verification |
|----|----------------|-------------------------------------|
| R1 | … | … |

## Open questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | […] | […] | […] |
