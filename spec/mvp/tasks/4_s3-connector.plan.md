---
status: DRAFT
spec_name: mvp
plan: 4
task_slug: s3-connector
git_branch: mvp/s3-connector
depends_on_tasks: [core-models]
blocks_tasks: [dlt-adapter]
---

# Plan: S3 source connector wiring

## Git branch

Branch: **`mvp/s3-connector`**

- [ ] Branch created from `main` after `mvp/core-models` merges.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Related spec

- Spec folder: `spec/mvp/`
- Design: `spec/mvp/DESIGN.md`
- Requirements: `spec/mvp/REQUIREMENTS.md`
- Root: `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`

When editing this plan, keep YAML aligned with **`.cursor/rules/spec-planning-enforcer.mdc`**: **`git_branch`**, **`task_slug`**, **`depends_on_tasks`**, **`blocks_tasks`**.

## Goal

Implement thin helpers in `dlk/connectors/` that translate a `SourceConfig` (type=s3) into dlt filesystem-oriented source/resource material the `DltAdapter` can attach to a pipeline. No I/O happens here — only configuration shaping.

## Definition of done

- [ ] `dlk/connectors/s3.py` exists with a function (e.g. `build_s3_source`) that accepts `SourceConfig` + `ExtractConfig` and returns dlt-compatible filesystem source configuration.
- [ ] Supports S3 path input.
- [ ] Supports glob patterns for multi-file reads.
- [ ] Supports explicit file format (CSV, JSONL, Parquet) via dlt filesystem readers; **JSON** is handled by adapter-driven **JSON→JSONL** preprocessing (`utils/`) before wiring the JSONL reader.
- [ ] Supports format inference from file extension when format not specified.
- [ ] Unit tests verify correct dlt resource shape for each variation.
- [ ] Connector does NOT perform any S3 I/O directly.
- [ ] `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Inter-task dependencies

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| `core-models` | `mvp/core-models` | `SourceConfig`, `ExtractConfig`, `FileFormat` types must exist |

**Blocks:** `dlt-adapter`.

**Parallel-safe with:** `sql-connector` (no shared files).

## Out of scope (this plan)

- Actual dlt pipeline execution.
- SQL source wiring.
- Destination logic.
- S3 incremental loading (open question in REQUIREMENTS).

## Steps

- [ ] **Step 1:** Research dlt's filesystem source API — confirm how to express S3 paths, glob patterns, and file format for the readers (csv, jsonl, parquet).
- [ ] **Step 2:** Create `dlk/connectors/s3.py` — `build_s3_source(source_config: SourceConfig, extract_config: ExtractConfig) -> ...` returning the dlt filesystem source/resource callable or config.
- [ ] **Step 3:** Handle explicit format selection from `SourceConfig.file_format`.
- [ ] **Step 4:** Implement format inference from file extension in `dlk/utils/format.py` (e.g. `.csv` → CSV, `.jsonl` → JSONL, `.json` → **JSON**, `.parquet` → Parquet) — used as fallback when format is not explicit.
- [ ] **Step 5:** Implement `json_document_to_jsonl` (or equivalent) in `dlk/utils/json_to_jsonl.py` per **`spec/mvp/DESIGN.md`** (stdlib `json` only; single object or array of objects).
- [ ] **Step 6:** Handle glob patterns (pass through to dlt filesystem source).
- [ ] **Step 7:** Add unit tests in `tests/connectors/test_s3.py` — mock dlt; assert correct shape for: single file explicit format, glob pattern, inferred format.
- [ ] **Step 8:** Add unit tests in `tests/utils/test_format.py` for format inference.
- [ ] **Step 9:** Add unit tests in `tests/utils/test_json_to_jsonl.py` for preprocessing (object, array of objects, invalid JSON, array of non-objects).
- [ ] **Step 10:** Verify: `uv run ruff check`, `uv run mypy dlk`, `uv run pytest`.

## Other dependencies

- **Requires:** Understanding of dlt's filesystem source API and readers.
- **External:** **`dataloadkit[filesystem]`** or **`[mvp]`** installed (see **`TECH.md`** / scaffold `pyproject.toml`).

## Affected files / modules

- `dlk/connectors/__init__.py`, `s3.py`
- `dlk/utils/format.py`, `json_to_jsonl.py`, `__init__.py`
- `tests/connectors/test_s3.py`
- `tests/utils/test_format.py`, `test_json_to_jsonl.py`

## Validation

### Automated

- `uv run pytest tests/connectors/test_s3.py tests/utils/test_format.py tests/utils/test_json_to_jsonl.py` — all pass
- `uv run mypy dlk/connectors dlk/utils` — zero errors

### Manual

- Review dlt filesystem resource output shape against dlt documentation.

## Notes

- Format inference is a shared utility (lives in `utils/`) since builders may also use it for validation or user feedback.
- If dlt filesystem source needs credentials at definition time, return a factory — same pattern as SQL connector.
