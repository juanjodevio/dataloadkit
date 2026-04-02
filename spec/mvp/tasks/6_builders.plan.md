---
status: DRAFT
spec_name: mvp
plan: 6
task_slug: builders
git_branch: mvp/builders
depends_on_tasks: [core-models, dlt-adapter]
blocks_tasks: [public-api]
---

# Plan: Fluent builders and .load() terminal

## Git branch

Branch: **`mvp/builders`**

- [ ] Branch created from `main` after `mvp/core-models` and `mvp/dlt-adapter` merge.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Related spec

- Spec folder: `spec/mvp/`
- Design: `spec/mvp/DESIGN.md`
- Requirements: `spec/mvp/REQUIREMENTS.md`
- Root: `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`

When editing this plan, keep YAML aligned with **`.cursor/rules/spec-planning-enforcer.mdc`**: **`git_branch`**, **`task_slug`**, **`depends_on_tasks`**, **`blocks_tasks`**.

## Goal

Implement the fluent builder layer (`dlk/builders/`) that collects user configuration through chained method calls, materializes a validated `LoadPlan`, and executes it via `DltAdapter`. After this task, a caller can manually instantiate a builder, configure a pipeline, and call `.load()` to run it end-to-end.

## Definition of done

- [ ] `SQLSourceBuilder` exists — accepts connection/table/query at construction; exposes `.to_sql()`, `.to_s3()`, `.to_sftp()` to set destination; exposes `.with_incremental()`, `.with_write_mode()`, `.with_primary_key()`, `.with_format()` modifiers; exposes `.load()` terminal.
- [ ] `S3SourceBuilder` exists — accepts S3 path/glob at construction; exposes same destination and modifier methods (minus SQL-only options like `.with_incremental()`).
- [ ] `.load()` validates config (via `core/validation`), builds `LoadPlan`, calls `DltAdapter.execute()`, returns `LoadResult`.
- [ ] Invalid state (missing destination, merge without PK, etc.) raises clear errors before execution.
- [ ] Fluent chain returns `self` (or a typed intermediate) at each step.
- [ ] Unit tests cover: full chain SQL→SQL, SQL→S3, SQL→SFTP, S3→SQL, S3→S3, S3→SFTP; modifier combinations; validation errors.
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `core-models` | `mvp/core-models` | All config types and validation |
| `dlt-adapter` | `mvp/dlt-adapter` | `DltAdapter.execute()` for `.load()` |

**Blocks:** `public-api`.

## Out of scope (this plan)

- Public `dlk.from_sql()` / `dlk.from_s3()` entry points (that's `public-api`).
- Integration tests with live infra.
- Advanced builder ergonomics (context managers, async, etc.).

## Steps

- [ ] **Step 1:** Create `dlk/builders/sql_source_builder.py` with `SQLSourceBuilder` class.
  - Constructor: `connection_string`, `table` (optional), `query` (optional), **`sql_dialect`** (required for SQL source: **`SqlDialect.REDSHIFT`** vs **`POSTGRES`**), `credentials` (optional).
  - Destination methods: `.to_sql(connection_string, dataset, table, sql_dialect=..., ...)` — **must set `DestinationConfig.sql_dialect`** (**`SqlDialect.REDSHIFT`** vs **`POSTGRES`**) per **`spec/mvp/tasks/5_dlt-adapter.plan.md`**; `.to_s3(bucket_url, ...)`, `.to_sftp(sftp_url, ...)` — each stores a `DestinationConfig` and returns `self`.
  - Modifier methods: `.with_incremental(cursor_field)`, `.with_write_mode(mode)`, `.with_primary_key(keys)`, `.with_format(fmt)` — each stores config and returns `self`.
  - Terminal: `.load()` → validate → `LoadPlan` → `DltAdapter.execute()` → `LoadResult`.
- [ ] **Step 2:** Create `dlk/builders/s3_source_builder.py` with `S3SourceBuilder` class.
  - Constructor: `path`, `file_format` (optional), `glob_pattern` (optional), `credentials` (optional).
  - Same destination and modifier methods (`.with_incremental()` may be omitted or raise NotImplementedError per open question in REQUIREMENTS).
  - Same `.load()` terminal.
- [ ] **Step 3:** Extract shared destination/modifier/load logic into a base or mixin if duplication is significant; keep it simple — favor composition per TECH.md.
- [ ] **Step 4:** In `.load()`, call `dlk.core.validation.validate_plan(plan)` before adapter execution; surface validation errors as clear exceptions.
- [ ] **Step 5:** Export builders from `dlk/builders/__init__.py`.
- [ ] **Step 6:** Add unit tests in `tests/builders/test_sql_source_builder.py` — chain construction, each modifier, each destination type, validation failures (no destination, merge without PK), mock adapter to verify LoadPlan shape.
- [ ] **Step 7:** Add unit tests in `tests/builders/test_s3_source_builder.py` — same coverage for S3 paths; include **`with_format("json")`** / inferred `.json` so `LoadPlan` carries format **json** for the adapter.
- [ ] **Step 8:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest`.

## Other dependencies

- **Requires:** `DESIGN.md` user flow (steps 2–11), `REQUIREMENTS.md` interface contract.

## Affected files / modules

- `dlk/builders/__init__.py`, `sql_source_builder.py`, `s3_source_builder.py`
- `tests/builders/test_sql_source_builder.py`, `test_s3_source_builder.py`

## Validation

### Automated

- `uv run pytest tests/builders/` — all pass
- `uv run mypy dlk/builders` — zero errors

### Manual

- In a REPL, construct a builder chain and inspect the LoadPlan before `.load()` fires (useful for debugging).

## Notes

- Builders should be stateless beyond the current chain — no global singletons or shared mutable state.
- Type hints on return values should enable IDE autocomplete for the fluent chain.
- Whether `.with_incremental()` on S3 raises immediately or at `.load()` time is a design choice — pick one and document; prefer fail-fast.
