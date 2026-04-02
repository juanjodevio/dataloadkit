---
status: DRAFT
spec_name: mvp
plan: 3
task_slug: sql-connector
git_branch: mvp/sql-connector
depends_on_tasks: [core-models]
blocks_tasks: [dlt-adapter]
---

# Plan: SQL source connector wiring

## Git branch

Branch: **`mvp/sql-connector`**

- [ ] Branch created from `main` after `mvp/core-models` merges.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Goal

Implement thin helpers in `dlk/connectors/` that translate a `SourceConfig` (type=sql) into dlt source/resource material the `DltAdapter` can attach to a pipeline. No I/O happens here — only configuration shaping for dlt's SQL source patterns.

## Definition of done

- [ ] `dlk/connectors/sql.py` exists with a function (e.g. `build_sql_source`) that accepts `SourceConfig` + `ExtractConfig` and returns dlt-compatible resource/source configuration.
- [ ] Supports table-based extraction (table name).
- [ ] Supports query-based extraction (raw SQL string).
- [ ] Supports incremental via cursor field when `ExtractConfig.incremental` is true.
- [ ] Supports primary key passthrough for merge write mode.
- [ ] Unit tests verify correct dlt resource shape for each mode (table, query, incremental, primary key).
- [ ] Connector does NOT perform any database I/O directly.
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `core-models` | `mvp/core-models` | `SourceConfig`, `ExtractConfig` types must exist |

**Blocks:** `dlt-adapter`.

**Parallel-safe with:** `s3-connector` (no shared files).

## Out of scope (this plan)

- Actual dlt pipeline execution (that's `dlt-adapter`).
- S3 source wiring.
- Destination logic.
- Chunked-read implementation (deferred to adapter or dlt native).

## Steps

- [ ] **Step 1:** Research dlt's `sql_database` source API — confirm how to express table, query, incremental, and primary key configuration for Redshift-compatible sources.
- [ ] **Step 2:** Create `dlk/connectors/__init__.py` with public exports.
- [ ] **Step 3:** Create `dlk/connectors/sql.py` — `build_sql_source(source_config: SourceConfig, extract_config: ExtractConfig) -> ...` returning the dlt resource/source callable or configuration dict the adapter will use.
- [ ] **Step 4:** Handle table vs query input branching.
- [ ] **Step 5:** Handle incremental configuration (attach `dlt.sources.incremental` or equivalent when cursor field is set).
- [ ] **Step 6:** Handle primary key passthrough.
- [ ] **Step 7:** Add unit tests in `tests/connectors/test_sql.py` — mock or stub dlt internals; assert correct configuration shape for: plain table, plain query, incremental table, table with primary key.
- [ ] **Step 8:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest`.

## Other dependencies

- **Requires:** Understanding of `dlt[redshift]` source API (sql_database source).
- **External:** dlt installed via `pyproject.toml` (from scaffold task).

## Affected files / modules

- `dlk/connectors/__init__.py`, `sql.py`
- `tests/connectors/test_sql.py`

## Validation

### Automated

- `uv run pytest tests/connectors/test_sql.py` — all pass
- `uv run mypy dlk/connectors` — zero errors

### Manual

- Review dlt resource output shape against dlt documentation.

## Notes

- The connector is a **configuration shaper**, not an executor. It must be testable without a live database.
- If dlt's sql_database source API requires connection at definition time, the connector may return a factory/callable instead — document the pattern for the adapter task.
