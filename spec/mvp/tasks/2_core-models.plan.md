---
status: DRAFT
spec_name: mvp
plan: 2
task_slug: core-models
git_branch: mvp/core-models
depends_on_tasks: [scaffold]
blocks_tasks: [sql-connector, s3-connector, dlt-adapter, builders]
---

# Plan: Core dataclass models and validation

## Git branch

Branch: **`mvp/core-models`**

- [ ] Branch created from `main` after `mvp/scaffold` merges.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Related spec

- Spec folder: `spec/mvp/`
- Design: `spec/mvp/DESIGN.md`
- Requirements: `spec/mvp/REQUIREMENTS.md`
- Root: `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`

When editing this plan, keep YAML aligned with **`.cursor/rules/spec-planning-enforcer.mdc`**: **`git_branch`**, **`task_slug`**, **`depends_on_tasks`**, **`blocks_tasks`**.

## Goal

Define the shared data model that every other module imports: `SourceConfig`, `DestinationConfig`, `ExtractConfig`, `LoadConfig`, `LoadPlan`, and `LoadResult` — all as stdlib `dataclasses` with explicit validation in `core/`. After this task, builders, connectors, and the adapter have stable types to code against.

## Definition of done

- [ ] `dlk/core/` contains dataclass definitions for `SourceConfig`, `DestinationConfig`, `ExtractConfig`, `LoadConfig`, `LoadPlan`.
- [ ] `dlk/results/` contains `LoadResult` dataclass with fields for row counts, execution metadata, and error info.
- [ ] Enums or literals defined for: source type (sql, s3), destination type (sql, s3, sftp), **SQL dialect** (**Redshift** vs **Postgres** for dlt destination selection per **`spec/mvp/tasks/5_dlt-adapter.plan.md`**), write mode (append, replace, merge), file format for S3 read (parquet, csv, jsonl, **json** where `json` triggers preprocessing per **`PRODUCT.md`**).
- [ ] Validation functions in `dlk/core/` enforce: required fields present, merge requires primary key, destination defined, **SQL source and SQL destination `sql_dialect`**, format valid for destination type.
- [ ] Unit tests cover happy-path construction and all validation error paths.
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `scaffold` | `mvp/scaffold` | Package structure and tooling must exist |

**Blocks:** `sql-connector`, `s3-connector`, `dlt-adapter`, `builders`.

## Out of scope (this plan)

- Builder logic or fluent API.
- dlt integration or adapter code.
- Connector wiring.
- Any I/O or network calls.

## Steps

- [ ] **Step 1:** Define enums/literals in `dlk/core/types.py`: `SourceType`, `DestinationType`, **`SqlDialect`** (`REDSHIFT`, `POSTGRES` — drives **`dlt.destinations.redshift`** vs **`dlt.destinations.postgres`**), `WriteMode`, `FileFormat`.
- [ ] **Step 2:** Define `SourceConfig` dataclass in `dlk/core/source_config.py` — fields: source type, connection string or S3 path, table/query, glob pattern, file format (optional: csv, parquet, jsonl, **json**), credentials (optional dict), **`sql_dialect: SqlDialect | None`** — **required** when `source_type == sql` (same **`SqlDialect`** enum as destinations: **Redshift** vs **PostgreSQL** for dlt source wiring).
- [ ] **Step 3:** Define `DestinationConfig` dataclass in `dlk/core/destination_config.py` — fields: destination type, connection string or path/URL, dataset name, table name, file format (optional for filesystem), credentials (optional dict), **`sql_dialect: SqlDialect | None`** — **required** when `destination_type == sql` (selects dlt Redshift vs Postgres destination); must be **`None`** when destination is not SQL.
- [ ] **Step 4:** Define `ExtractConfig` dataclass in `dlk/core/extract_config.py` — fields: incremental (bool), cursor field (optional), chunk size (optional), primary key (optional list of str).
- [ ] **Step 5:** Define `LoadConfig` dataclass in `dlk/core/load_config.py` — fields: write mode (default append), partitioning (optional).
- [ ] **Step 6:** Define `LoadPlan` dataclass in `dlk/core/plan.py` — composes `SourceConfig`, `DestinationConfig`, `ExtractConfig`, `LoadConfig`, plus pipeline name.
- [ ] **Step 7:** Define `LoadResult` dataclass in `dlk/results/result.py` — fields: success (bool), row count (optional int), execution time (optional float), error message (optional str), raw metadata (optional dict).
- [ ] **Step 8:** Write validation functions in `dlk/core/validation.py` — validate a `LoadPlan` before execution (merge needs PK, destination required, **SQL sources and SQL destinations require `sql_dialect`**, filesystem format valid, incremental needs cursor field, etc.).
- [ ] **Step 9:** Export public types from `dlk/core/__init__.py` and `dlk/results/__init__.py`.
- [ ] **Step 10:** Add unit tests: `tests/core/test_models.py` (construction, defaults, field types) and `tests/core/test_validation.py` (each validation rule, both pass and fail).
- [ ] **Step 11:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest`.

## Other dependencies

- **Requires:** `DESIGN.md` data model section, `REQUIREMENTS.md` data requirements.

## Affected files / modules

- `dlk/core/types.py`, `source_config.py`, `destination_config.py`, `extract_config.py`, `load_config.py`, `plan.py`, `validation.py`, `__init__.py`
- `dlk/results/result.py`, `__init__.py`
- `tests/core/test_models.py`, `test_validation.py`

## Validation

### Automated

- `uv run pytest tests/core/` — all pass
- `uv run mypy dlk/core dlk/results` — zero errors
- `uv run ruff check` — zero errors

### Manual

- Instantiate each dataclass in a REPL; confirm repr, defaults, and type annotations behave as expected.

## Notes

- Keep fields minimal for MVP; avoid premature options that no builder exposes yet.
- `LoadResult.raw_metadata` is an escape hatch for dlt info; whether to populate it is an open question in REQUIREMENTS — include the field, leave population to the adapter task.
- Credential dicts are pass-through; dlk does not interpret or persist them (security baseline in TECH.md).
