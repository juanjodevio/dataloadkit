---
status: DRAFT
---

# Tech

## Core Technologies

### Backend
- Language: Python **3.9.2** through **3.14.x** (upper bound below **3.15**, matching **`dlt`**’s `requires-python`; CI exercises **3.9** and **latest stable**)
- Framework: None (library-first design)
- Database: 
  - Source: **Amazon Redshift** and **PostgreSQL** (MVP SQL sources)
  - Destination: **Redshift** and **PostgreSQL** (via dlt’s respective destinations)
- ORM / query layer:
  - SQLAlchemy (connection abstraction only)
  - optional: redshift_connector / psycopg2
- Auth:
  - Environment-based credentials
  - AWS IAM (preferred)
  - connection strings for SQL
- Storage:
  - Amazon S3 (primary)
  - SFTP (via dlt filesystem / fsspec)

---

### Infrastructure & DevOps
- IaC:
  - Optional future: Terraform for examples
- CI/CD:
  - GitHub Actions
- Containers:
  - Optional for development and testing

---

### Third-party services
- dlt (core execution engine); **PostgreSQL** drivers (e.g. via **`dlt[postgres]`**) and **Redshift** (via **`dlt[redshift]`**) come from optional extras (see **Optional dependencies**)
- fsspec (filesystem abstraction)
- boto3 (AWS access)

---

## Development Tools

- Python package manager:
  - uv (lockfile, environments, `uv sync` / `uv run`)
- Linting / formatting:
  - ruff (lint + format)
- Type checking:
  - mypy
- Testing:
  - pytest (e.g. `uv run pytest`)
- Build / publish:
  - `uv build` (PEP 517 backend defined in `pyproject.toml`, e.g. hatchling)

---

## Environment Strategy

- Default configuration via environment variables
- Support explicit configuration overrides in API
- No internal config persistence

Environments:
- local: developer machine (.env supported)
- CI: GitHub Actions environment variables
- production: user-managed (library consumer responsibility)

---

## Development Workflow

1. Work from `spec/{spec}/tasks/N_<task-slug>.plan.md`; create Git branch `{spec}/{task-slug}` (must match the plan's `git_branch` frontmatter)
2. Implement feature within module boundaries
3. Add unit tests
4. Add integration tests if applicable
5. Run linting, typing, and tests
6. Open PR
7. Merge to main after review

---

## Security Baseline

- Never store credentials in code
- Avoid logging sensitive information
- Prefer IAM-based authentication for AWS
- Support secure SFTP authentication (key-based preferred)
- Validate external inputs (paths, queries, configs)
- Ensure dependency updates are monitored

---

## Observability

- Logging:
  - Python standard logging
  - structured logs where useful

- Metrics:
  - expose execution metadata via LoadResult

- Error handling:
  - clear, actionable error messages
  - propagate underlying dlt errors with context

---

## Technical Constraints

- dlt is the only execution engine
- All data movement must go through dlt pipelines
- No custom execution engines or transfer logic
- SFTP must be handled via dlt filesystem destination
- Library must remain lightweight (no heavy runtime dependencies)
- Python-only (no multi-language support)
- Source wiring lives in **`connectors/`** (per `STRUCTURE.md`): translate `SourceConfig` into dlt source/resource material; **`adapters/`** owns execution and composes connectors + dlt—no second extract path

---

## Coding Preferences

- Use type hints everywhere
- **Config and plan models:** use **`dataclasses`** (stdlib) for `SourceConfig`, `DestinationConfig`, `LoadPlan`, and related types; keep validation explicit in `core/` (no Pydantic as a **required** dlk dependency for these models)
- Favor composition over inheritance
- Avoid hidden side effects
- Keep public API minimal and stable
- Use fluent builder pattern for API

---

## Testing Expectations

### Unit Tests
- Required for all core modules
- Builders, core models, utilities

### Integration Tests
- Required for:
  - SQL → SQL
  - SQL → S3
  - S3 → SQL
  - SQL/S3 → SFTP

- Use real or controlled test environments where possible

---

## Deployment Model

- Distributed as a Python package via PyPI
- Installed via pip, uv, or other standards-compliant installers
- No runtime services or infrastructure required
- Execution occurs within user environment

---

## Optional dependencies (dlt extras)

`dataloadkit` maps **dlt’s optional stacks** to **`[project.optional-dependencies]`** in `pyproject.toml` so installs stay explicit and match dlt’s own extra names:

| Extra on `dataloadkit` | Pulls (PEP 508) | Use when |
|------------------------|-----------------|----------|
| `redshift` | `dlt[redshift]` | **Redshift** SQL sources and destinations |
| `postgres` | `dlt[postgres]` | **PostgreSQL** SQL sources and destinations ([dlt Postgres](https://dlthub.com/docs/dlt-ecosystem/destinations/postgres)) |
| `filesystem` | `dlt[filesystem]` | S3 (and other filesystem) sources/destinations via dlt filesystem |
| `sftp` | `dlt[sftp]` | SFTP URLs with filesystem destination ([paramiko](https://dlthub.com/docs/dlt-ecosystem/destinations/filesystem)) |
| `mvp` | `dlt[redshift,postgres,filesystem,sftp]` | Full **MVP** surface in **`PRODUCT.md`**—**Redshift + PostgreSQL + S3 + SFTP** (recommended default for library consumers) |

- **Base** runtime dependency: pin **`dlt`** with a floor version only (no brackets in `dependencies`); consumers choose extras, or install **`dataloadkit[mvp]`** for the documented MVP.
- **Development / CI:** use **`uv sync --extra mvp`** (or `--all-extras` if you want every optional stack resolvable in the lockfile) so tests and examples match MVP scope.
- Do not duplicate ad-hoc `dlt[...]` strings in docs without pointing to these named extras.

---

## Notes

- dlt must be isolated within the **adapter** layer; **`connectors/`** only shapes dlt sources from config (see `STRUCTURE.md`) and is invoked from the adapter, not as a parallel runtime
- filesystem destinations (S3, SFTP) must behave consistently
- avoid introducing additional abstraction layers unless necessary
- prioritize developer experience over configurability
- maintain clear separation between:
  - configuration
  - planning
  - execution