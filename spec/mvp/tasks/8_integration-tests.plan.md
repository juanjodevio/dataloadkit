---
status: DRAFT
spec_name: mvp
plan: 8
task_slug: integration-tests
git_branch: mvp/integration-tests
depends_on_tasks: [public-api]
blocks_tasks: []
---

# Plan: Integration tests and examples

## Git branch

Branch: **`mvp/integration-tests`**

- [ ] Branch created from `main` after `mvp/public-api` merges.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Related spec

- Spec folder: `spec/mvp/`
- Design: `spec/mvp/DESIGN.md`
- Requirements: `spec/mvp/REQUIREMENTS.md`
- Root: `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`

When editing this plan, keep YAML aligned with **`.cursor/rules/spec-planning-enforcer.mdc`**: **`git_branch`**, **`task_slug`**, **`depends_on_tasks`**, **`blocks_tasks`**.

## Goal

Validate every MVP acceptance path end-to-end against real or controlled test infrastructure, and provide usage examples. After this task, the MVP release standard from `PRODUCT.md` is demonstrably met.

## Definition of done

- [ ] Integration tests exist for: SQL→SQL, SQL→S3, S3→SQL, SQL/S3→SFTP (the four paths in `PRODUCT.md` MVP release standard).
- [ ] Tests for incremental loading (SQL source with cursor field).
- [ ] Tests for write modes: append, replace, merge.
- [ ] Each test verifies that `.load()` returns a `LoadResult` with expected fields.
- [ ] Edge-case tests: empty dataset, missing credentials (error message quality), invalid SQL query.
- [ ] `examples/` contains at least one runnable example per MVP path with inline comments.
- [ ] A short `README.md` in `examples/` explains how to configure credentials and run examples.
- [ ] CI integration test job defined (may be gated behind an environment/secret flag).
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green (unit tests still pass).

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `public-api` | `mvp/public-api` | Full library must be wired end-to-end |

**Blocks:** none — this is the final MVP task.

## Out of scope (this plan)

- Performance benchmarking.
- Stress/load testing.
- SFTP-as-source tests (out of MVP scope).
- Automated infra provisioning (tests assume existing test resources).

## Steps

- [ ] **Step 1:** Set up test infrastructure or document required test resources: a Redshift/Postgres-compatible database, an S3 bucket, an SFTP server (can use a local Docker SFTP container for CI).
- [ ] **Step 2:** Create `tests/integration/conftest.py` with fixtures for: SQL connection string, S3 bucket URL, SFTP URL, test table seeding, cleanup.
- [ ] **Step 3:** Create `tests/integration/test_sql_to_sql.py` — load from SQL table to SQL destination; verify rows arrive; test append and replace modes.
- [ ] **Step 4:** Create `tests/integration/test_sql_to_s3.py` — load from SQL table to S3; verify file(s) written in expected format.
- [ ] **Step 5:** Create `tests/integration/test_s3_to_sql.py` — load from S3 file(s) to SQL destination; verify rows arrive; test CSV, JSONL, Parquet, and **JSON** (`.json` object and array-of-objects) inputs with **JSON→JSONL** preprocessing.
- [ ] **Step 6:** Create `tests/integration/test_to_sftp.py` — load from SQL and S3 to SFTP; verify file(s) written.
- [ ] **Step 7:** Create `tests/integration/test_incremental.py` — SQL source with `with_incremental(cursor_field)`; run twice; verify second run loads only new rows.
- [ ] **Step 8:** Create `tests/integration/test_merge.py` — SQL source with `with_write_mode("merge")` and `with_primary_key([...])`; verify upsert behavior.
- [ ] **Step 9:** Create `tests/integration/test_edge_cases.py` — empty dataset, invalid query error, missing credentials error.
- [ ] **Step 10:** Create example scripts in `examples/`: `sql_to_sql.py`, `sql_to_s3.py`, `s3_to_sql.py`, `to_sftp.py` — each a short, self-contained script using `dlk.from_*().to_*().load()`.
- [ ] **Step 11:** Write `examples/README.md` with setup instructions (credentials, test data, expected output).
- [ ] **Step 12:** Add or update `.github/workflows/ci.yml` — integration test job that runs `pytest tests/integration/` (gated on secrets availability or manual trigger).
- [ ] **Step 13:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` (unit + integration where infra is available).

## Other dependencies

- **Requires:** Test infrastructure — Postgres (or Redshift), S3 bucket, SFTP server.
- **External:** CI secrets for database/S3/SFTP credentials; Docker for local SFTP.

## Affected files / modules

- `tests/integration/` (all new)
- `examples/` (all new)
- `.github/workflows/ci.yml` (updated)

## Validation

### Automated

- `uv run pytest tests/integration/` — all pass against test infra
- `uv run pytest tests/` — all unit + integration green
- CI workflow green

### Manual

- Run each example script locally and confirm data arrives at the destination.
- Verify `LoadResult` output is readable and contains row counts.

## Notes

- Integration tests are inherently environment-dependent; mark them with `@pytest.mark.integration` and skip in CI if credentials are absent.
- For SFTP, a Docker-based SFTP server (e.g. `atmoz/sftp`) is the simplest CI-friendly option.
- Postgres can substitute for Redshift in tests for most scenarios; document any Redshift-specific behaviors that differ.
- Examples should be copy-pasteable — avoid imports from test utilities.
