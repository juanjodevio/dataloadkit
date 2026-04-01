---
status: DRAFT
---

# Technology

Replace bracketed placeholders. Remove sections that do not apply. This file captures **technical choices, constraints, and standards** for the repository. Product intent belongs in `PRODUCT.md`; layout and ownership in `STRUCTURE.md`.

## Technical Summary

[One short paragraph: architecture style, runtime model, and priorities—for example developer velocity, reliability, compliance, cost.]

## Decision Principles

- [Principle 1 — e.g. prefer boring, proven defaults for core systems.]
- [Principle 2 — e.g. optimize for maintainability.]
- [Principle 3 — e.g. managed services when ops burden is high.]
- [Principle 4 — e.g. explicit contracts at system boundaries.]

## Stack Baseline

Update the table as you lock choices.

| Area | Standard choice | Version policy | Notes |
|---|---|---|---|
| Language(s) | [e.g. TypeScript, Python] | [pin policy] | |
| Runtime(s) | [e.g. Node.js LTS] | [LTS policy] | |
| API / backend framework | [e.g. FastAPI, NestJS] | [upgrade cadence] | |
| Web frontend | [e.g. Next.js, Vite + React] | [policy] | |
| ORM / data access | [e.g. Prisma, SQLAlchemy] | [policy] | |
| Database | [e.g. PostgreSQL] | [managed vs self-hosted] | |
| Auth | [e.g. provider, session model] | [policy] | |
| Object / file storage | [e.g. S3-compatible] | [policy] | |
| Async / jobs / queues | [e.g. Edge Functions, SQS, Celery] | [policy] | |
| IaC | [e.g. Terraform, Pulumi] | [policy] | |
| Hosting | [e.g. Vercel, k8s, VMs] | [regions, envs] | |
| CI/CD | [e.g. GitHub Actions] | [required checks] | |
| Containers | [Docker, Compose — yes/no] | [policy] | |

## Core Technologies (narrative)

### Backend

- [Language, framework, API style.]
- [Database, migrations tool, ORM.]
- [AuthN/AuthZ approach.]
- [Background work: queues, workers, serverless — and what you explicitly do *not* use unless an ADR says otherwise.]

### Frontend

- [Framework, bundler, UI kit.]
- [Styling, state, data fetching, forms.]
- [PWA / offline / installable — only if in scope; align with `PRODUCT.md` and `spec/<spec_name>/`.]

### Infrastructure & DevOps

- [IaC, hosting, environments, deploy targets.]
- [How local dev is run: Compose, devcontainers, etc.]

### AI / External Services (if applicable)

- [LLM provider and versioning policy.]
- [Other APIs: speech, payments, email — pin and document.]
- [Observability vendors: errors, APM, session replay — with privacy review if needed.]

## Development Tools

- **Package managers:** [e.g. pnpm, uv, pip]
- **Lint / format:** [list]
- **Type checking:** [list]
- **Testing:** [unit, integration, e2e tools]
- **API contracts:** [OpenAPI, GraphQL schema, etc.]

## Environment Strategy

- **Local:** [how to run; `.env` from `.env.example`; never commit secrets.]
- **Staging / production:** [separate projects, secrets, promotion rules.]
- **Configuration:** [e.g. typed settings server-side; public env vars naming for clients.]

## Development process

- [Branching and PR expectations.]
- [Infra: plan/review before apply if IaC.]
- [Migrations: single source of truth — e.g. Alembic only, or vendor migrations only; state the rule once tooling exists.]
- [UI generation / codegen rules if used — must pass lint and review.]

## Architecture and Boundaries

- **Layering:** [presentation → application → domain → adapters — adjust to your layout in `STRUCTURE.md`.]
- **Integration rule:** [external systems behind adapters.]
- **Alignment:** implementation follows `STRUCTURE.md` module boundaries unless an ADR changes them.

## API and Contract Standards

- **Style:** [REST / GraphQL / RPC]
- **Documentation source of truth:** [where clients consume schemas]
- **Errors:** [envelope, codes]
- **Versioning:** [strategy]

## Security Baseline

- [Secrets handling.]
- [AuthZ model and where policies live.]
- [Encryption in transit / at rest expectations.]
- [Sensitive data classification — align with `PRODUCT.md`.]
- [Dependency scanning in CI if used.]

## Observability

- **Logging:** [structured, correlation IDs, redaction.]
- **Metrics:** [health, golden signals when applicable.]
- **Tracing:** [when to adopt OpenTelemetry or similar.]
- **Errors:** [tooling, PII scrubbing.]

## Reliability and Operational Targets (NFR)

| Attribute | Target | Measurement | Notes |
|---|---|---|---|
| Availability | [e.g. 99.9%] | [where measured] | |
| P95 latency | […] | […] | |
| Error rate | […] | […] | |
| RPO / RTO | […] | […] | |
| Background jobs | […] | […] | [timeouts, platform limits] |

## Technical Constraints

- [Constraint tied to `PRODUCT.md` — e.g. regulatory, tenancy, AI assistive-only.]
- [Stack constraint: “do not introduce X without ADR.”]
- [Performance or cost guardrails.]

## Coding Preferences

- [Language-specific conventions.]
- [Avoid `any` at boundaries; public APIs typed.]
- [Feature behavior defined in `PRODUCT.md` and `spec/<spec_name>/`, not only in comments.]

## Testing Expectations

- **Unit:** [scope.]
- **Integration:** [DB, external sandboxes.]
- **E2E:** [critical paths when UI exists.]
- [Same-change rule for tests when logic changes.]

## ADRs (Architecture Decision Records)

Record reversals and big bets (new queue system, new cloud, etc.).

### ADR Index

| ADR | Status | Decision | Notes |
|---|---|---|---|
| ADR-001 | [Proposed / Accepted / Deprecated] | [short title] | [optional] |

### ADR Template

```markdown
# ADR-XXX: [Decision title]

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-YYY

## Context
[What problem or constraint requires this decision?]

## Options Considered
- [Option A]
- [Option B]

## Decision
[Chosen option and rationale]

## Consequences
### Positive
- [...]

### Negative
- [...]

### Follow-up Actions
- [ ] [...]
```

Store full ADR files under `docs/decisions/` if you use that layout (see `STRUCTURE.md`).

## Open Technical Questions

| # | Question | Owner | Target date |
|---|---|---|---|
| 1 | […] | […] | […] |

## Related Documents

- `README.md` — setup, commands, contribution
- `PRODUCT.md` — product intent, scope, outcomes
- `STRUCTURE.md` — repository layout, boundaries, ownership
- `spec/` — per-feature planning (`DESIGN.md` → `REQUIREMENTS.md` with EARS where applicable → `tasks/N_*.plan.md`); Cursor: `@spec`
- `.cursor/BUGBOT.md` — [Cursor Bugbot](https://cursor.com/docs/bugbot) PR review context (optional; enable Bugbot in the [Cursor dashboard](https://cursor.com/dashboard/integrations))
