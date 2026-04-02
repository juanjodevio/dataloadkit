---
status: DRAFT
spec_name: mvp
plan: 7
task_slug: public-api
git_branch: mvp/public-api
depends_on_tasks: [builders]
blocks_tasks: [integration-tests]
---

# Plan: Public API entry points

## Git branch

Branch: **`mvp/public-api`**

- [ ] Branch created from `main` after `mvp/builders` merges.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Related spec

- Spec folder: `spec/mvp/`
- Design: `spec/mvp/DESIGN.md`
- Requirements: `spec/mvp/REQUIREMENTS.md`
- Root: `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`

When editing this plan, keep YAML aligned with **`.cursor/rules/spec-planning-enforcer.mdc`**: **`git_branch`**, **`task_slug`**, **`depends_on_tasks`**, **`blocks_tasks`**.

## Goal

Expose the stable, user-facing entry points `dlk.from_sql(...)` and `dlk.from_s3(...)` in `dlk/api/` and re-export them from `dlk/__init__.py`. After this task, users interact with dlk exactly as described in DESIGN.md and REQUIREMENTS.md: `import dlk; dlk.from_sql(...).to_s3(...).load()`.

## Definition of done

- [ ] `dlk/api/entrypoints.py` (or similar) defines `from_sql(...)` and `from_s3(...)` functions that return the appropriate builder.
- [ ] `from_sql` accepts at minimum: `connection_string`, `table` (optional), `query` (optional), `credentials` (optional).
- [ ] `from_s3` accepts at minimum: `path`, `file_format` (optional), `credentials` (optional).
- [ ] `dlk/__init__.py` re-exports `from_sql` and `from_s3` so `import dlk; dlk.from_sql(...)` works.
- [ ] Docstrings on public functions with clear parameter descriptions.
- [ ] Unit tests verify: `dlk.from_sql(...)` returns `SQLSourceBuilder`, `dlk.from_s3(...)` returns `S3SourceBuilder`, full chain `dlk.from_sql(...).to_sql(...).load()` calls through correctly.
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `builders` | `mvp/builders` | Builder classes must exist |

**Blocks:** `integration-tests`.

## Out of scope (this plan)

- Builder internals (already done).
- Adapter internals (already done).
- Integration tests with live infra.
- Additional convenience functions beyond `from_sql` and `from_s3`.

## Steps

- [ ] **Step 1:** Create `dlk/api/entrypoints.py` — `from_sql(...)` instantiates and returns `SQLSourceBuilder`; `from_s3(...)` instantiates and returns `S3SourceBuilder`.
- [ ] **Step 2:** Add clear docstrings with parameter types and short usage example in each function.
- [ ] **Step 3:** Export from `dlk/api/__init__.py`.
- [ ] **Step 4:** Update `dlk/__init__.py` — re-export `from_sql`, `from_s3`, `__version__`, and key types (`LoadResult`) for convenience.
- [ ] **Step 5:** Add unit tests in `tests/api/test_entrypoints.py` — verify return types, parameter forwarding, full chain with mocked adapter.
- [ ] **Step 6:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest`.

## Other dependencies

- **Requires:** `DESIGN.md` user flow, `REQUIREMENTS.md` interface contract.

## Affected files / modules

- `dlk/api/__init__.py`, `entrypoints.py`
- `dlk/__init__.py`
- `tests/api/test_entrypoints.py`

## Validation

### Automated

- `uv run pytest tests/api/` — all pass
- `uv run mypy dlk/api` — zero errors

### Manual

- `python -c "import dlk; print(dlk.from_sql)"` — confirms the function is importable from the top-level package.

## Notes

- This is intentionally a small task — the public surface should stay minimal per TECH.md ("keep public API minimal and stable").
- Avoid importing heavy dlt modules at `dlk.__init__` import time if possible; defer to `.load()`.
