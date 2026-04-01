---
status: DRAFT
---

# Structure

Replace bracketed placeholders. Keep this document about **how the repository is organized** and where responsibilities live. Keep product intent in `PRODUCT.md` and technical decisions in `TECH.md`.

## Repository Purpose

[One short paragraph describing what this repository contains and what it does not contain.]

## Top-Level Layout

Update this tree to match the real repo. Delete paths you do not use.

```text
/
├─ README.md
├─ PRODUCT.md
├─ STRUCTURE.md
├─ TECH.md
├─ spec/                    # Per-feature: spec/<name>/DESIGN → REQUIREMENTS (EARS) → tasks/N_*.plan.md; Cursor: @spec
├─ docs/
│  ├─ decisions/            # ADRs (optional)
│  └─ runbooks/             # Operational guides (optional)
├─ apps/                    # Deployable apps (web/api/worker)
│  ├─ web/
│  ├─ api/
│  └─ worker/
├─ packages/                # Shared libraries/modules (monorepo)
│  ├─ ui/
│  ├─ domain/
│  ├─ data-access/
│  └─ utils/
├─ services/                # Alternative to apps/, if service-oriented
├─ infra/                   # Infrastructure as code, environments
├─ scripts/                 # Build/dev/release scripts
├─ tests/                   # Cross-cutting tests (if centralized)
└─ .cursor/
   ├─ rules/                 # Cursor agent rules (*.mdc)
   └─ BUGBOT.md              # Cursor Bugbot PR review context (optional)
```

## Architecture Mapping (Logical)

Map logical layers to physical directories.

| Logical layer | Responsibility | Primary path(s) |
|---|---|---|
| Product/UI | [Screens, user flows, interaction logic] | `[apps/web]` |
| Application/API | [Use cases, API handlers, orchestration] | `[apps/api]` |
| Domain | [Core entities, invariants, policies] | `[packages/domain]` |
| Data/Integration | [DB access, external providers, adapters] | `[packages/data-access]` |
| Infrastructure | [Deploy, provisioning, runtime config] | `[infra]` |

## Module Boundaries and Dependency Rules

Define what each major area can import/call.

- **[UI]** may depend on **[application/domain contracts]**, but not directly on **[infra internals]**.
- **[Domain]** must stay framework-agnostic and avoid runtime-specific concerns.
- **[Data adapters]** implement interfaces defined by **[domain/application]** where possible.
- **Cross-module imports** should follow one direction: `[presentation] -> [application] -> [domain] -> [adapters]`.

If you use lint rules or tooling to enforce boundaries, list them here.

## Directory Contracts

For each key directory, define purpose, allowed contents, and anti-patterns.

### `[path/to/area]`

- **Purpose:** [Why this directory exists.]
- **Must contain:** [Expected file types or module types.]
- **Must not contain:** [Disallowed concerns.]
- **Owner:** [Team/person/role.]

### `[path/to/another-area]`

- **Purpose:** [...]
- **Must contain:** [...]
- **Must not contain:** [...]
- **Owner:** [...]

## Naming Conventions

- **Directories:** `[kebab-case | snake_case | other]`
- **Files:** `[pattern]` (examples: `*.service.ts`, `*_test.py`, `*.spec.ts`)
- **Symbols:** `[PascalCase for types, camelCase for functions, etc.]`
- **Tests:** [Where test files live and naming rules.]

## Specs and Documentation Placement

Define where living docs belong so contributors know where to update.

- Product intent and scope: `PRODUCT.md`
- Repository organization and ownership: `STRUCTURE.md`
- Tech stack, ADRs, operational constraints: `TECH.md`
- Spec planning folders: **`spec/<spec_name>/`** — `DESIGN.md`, `REQUIREMENTS.md` (EARS where applicable), **`tasks/N_<task>.plan.md`** (see `spec/README.md`; Cursor: **`@spec`**)
- Runbooks and incident docs: `[docs/runbooks/]`

## Environment and Configuration Layout

- **Environment files:** `[.env, .env.example, config/*]`
- **Secret handling:** [Where secrets are referenced; never committed policy.]
- **Per-environment config:** `[dev/staging/prod paths]`

## Build, Test, and Release Surfaces

- **Build entrypoints:** `[commands or scripts path]`
- **Test entrypoints:** `[unit/integration/e2e commands]`
- **Release/deploy entrypoints:** `[pipeline files or scripts]`
- **Artifact outputs:** `[dist/, build/, images, packages]`

## Ownership and Review Map

Optional but recommended for multi-area repos.

| Area | Owner | Reviewer(s) | Notes |
|---|---|---|---|
| `[apps/web]` | [@team-or-person] | [@team-or-person] | [critical context] |
| `[apps/api]` | [...] | [...] | [...] |
| `[infra]` | [...] | [...] | [...] |

## Change Checklist for Structural Updates

When adding/moving/removing modules or directories:

- [ ] Update the top-level tree in this file.
- [ ] Update boundary rules if dependency direction changes.
- [ ] Update ownership mapping.
- [ ] Update related docs (`README.md`, `TECH.md`, relevant `spec/<spec_name>/` files).
- [ ] Verify build/test/release entrypoints still work.

## Open Questions

| # | Question | Owner | Target date |
|---|---|---|---|
| 1 | [...] | [...] | [...] |
| 2 | [...] | [...] | [...] |

## Related Documents

- `README.md` — project overview and quickstart
- `PRODUCT.md` — product intent, scope, and outcomes
- `TECH.md` — technical decisions, stack, and operational constraints
- `spec/<spec_name>/` — per-feature **`DESIGN.md` → `REQUIREMENTS.md` (EARS) → `tasks/N_*.plan.md`**; see `spec/README.md`; Cursor: **`@spec`**
