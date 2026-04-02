---
status: DRAFT
spec_name: mvp
plan: 5
task_slug: dlt-adapter
git_branch: mvp/dlt-adapter
depends_on_tasks: [core-models, sql-connector, s3-connector]
blocks_tasks: [builders]
---

# Plan: DltAdapter — pipeline execution engine

## Git branch

Branch: **`mvp/dlt-adapter`**

- [ ] Branch created from `main` after `mvp/core-models`, `mvp/sql-connector`, and `mvp/s3-connector` all merge.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Goal

Implement `DltAdapter` in `dlk/adapters/` — the single execution engine that receives a validated `LoadPlan`, composes a dlt pipeline (source from connectors + destination), runs it, and returns a `LoadResult`. After this task, any code that can build a `LoadPlan` can execute a real data load.

## Definition of done

- [ ] `dlk/adapters/dlt_adapter.py` exists with a class or function (e.g. `DltAdapter.execute(plan: LoadPlan) -> LoadResult`).
- [ ] Adapter uses `dlk/connectors/sql.py` for SQL sources and `dlk/connectors/s3.py` for S3 sources.
- [ ] Adapter maps `DestinationConfig` to the correct dlt destination: SQL (database), S3 (filesystem), SFTP (filesystem with SFTP protocol).
- [ ] Adapter maps `LoadConfig.write_mode` to dlt write disposition (append, replace, merge).
- [ ] Adapter passes credentials through to dlt without persisting or logging them.
- [ ] Adapter converts dlt execution output into `LoadResult` (success, row count, timing, error).
- [ ] On dlt failure, adapter wraps the error with enough context and raises or returns it.
- [ ] Unit tests with mocked dlt verify: source selection, destination mapping, write mode mapping, error wrapping.
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `core-models` | `mvp/core-models` | `LoadPlan`, `LoadResult`, all config types |
| `sql-connector` | `mvp/sql-connector` | `build_sql_source` |
| `s3-connector` | `mvp/s3-connector` | `build_s3_source` |

**Blocks:** `builders` (which call the adapter from `.load()`).

## Out of scope (this plan)

- Builder or public API logic.
- Credential management or secret storage.
- Retry logic beyond what dlt provides natively.
- Custom logging framework (use stdlib `logging`).

## Steps

- [ ] **Step 1:** Create `dlk/adapters/dlt_adapter.py` with `DltAdapter` class and `execute(plan: LoadPlan) -> LoadResult` method.
- [ ] **Step 2:** Implement source resolution: dispatch to `build_sql_source` or `build_s3_source` based on `plan.source_config.source_type`.
- [ ] **Step 3:** Implement destination resolution — map `DestinationType.sql` to `dlt.destinations.postgres` (or Redshift-compatible), `DestinationType.s3` to `dlt.destinations.filesystem` with S3 bucket URL, `DestinationType.sftp` to `dlt.destinations.filesystem` with SFTP URL.
- [ ] **Step 4:** Map `LoadConfig.write_mode` → dlt write disposition string (`append`, `replace`, `merge`).
- [ ] **Step 5:** Compose `dlt.pipeline(...)` with pipeline name from `LoadPlan`, destination, and dataset name from `DestinationConfig`.
- [ ] **Step 6:** Run pipeline with the source resource; capture dlt load info.
- [ ] **Step 7:** Convert dlt load info into `LoadResult` — extract row counts, timing, errors.
- [ ] **Step 8:** Wrap dlt exceptions with contextual error messages; ensure no credential leakage in error output.
- [ ] **Step 9:** Add stdlib `logging` calls at key points (plan received, pipeline started, execution complete/failed).
- [ ] **Step 10:** Export from `dlk/adapters/__init__.py`.
- [ ] **Step 11:** Add unit tests in `tests/adapters/test_dlt_adapter.py` — mock `dlt.pipeline`, connectors; verify: SQL source dispatch, S3 source dispatch, each destination type, each write mode, error wrapping, LoadResult population.
- [ ] **Step 12:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest`.

## Other dependencies

- **Requires:** dlt installed with `[redshift,filesystem]` extras.
- **External:** No live infra needed for unit tests (mock dlt).

## Affected files / modules

- `dlk/adapters/__init__.py`, `dlt_adapter.py`
- `tests/adapters/test_dlt_adapter.py`

## Validation

### Automated

- `uv run pytest tests/adapters/` — all pass
- `uv run mypy dlk/adapters` — zero errors

### Manual

- (Deferred to integration-tests task for live execution.)

## Notes

- SFTP destination uses the same `dlt.destinations.filesystem` as S3 but with an `sftp://` URL — confirm dlt/fsspec support during implementation.
- Filesystem destination format (parquet, csv, jsonl) comes from `DestinationConfig.file_format`; pass to dlt's `loader_file_format` parameter.
- Partitioning support for S3 destination (REQUIREMENTS optional feature) — include the parameter passthrough if dlt supports it simply; otherwise note as follow-up.
